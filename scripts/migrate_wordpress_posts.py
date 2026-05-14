#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import html
import json
import os
import pty
import re
import subprocess
import sys
import urllib.error
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

import requests
from github import Github
from github.GithubException import GithubException, UnknownObjectException

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main as blog_main

WORDPRESS_SITE = "pacoxu.wordpress.com"
WORDPRESS_API = f"https://public-api.wordpress.com/rest/v1.1/sites/{WORDPRESS_SITE}/posts/"
BLOG_LABEL = "Blog"
MAX_ISSUE_BODY_LENGTH = 62000
PAGE_SIZE = 100
MIGRATION_SOURCE = "pacoxu.wordpress.com"


class HtmlSanitizer(HTMLParser):
    ALLOWED_TAGS = {
        "a",
        "blockquote",
        "br",
        "code",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "img",
        "li",
        "ol",
        "p",
        "pre",
        "strong",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "ul",
    }
    VOID_TAGS = {"br", "hr", "img"}
    UNWRAP_TAGS = {"div", "figure", "figcaption", "section", "span"}
    ALLOWED_ATTRS = {
        "a": {"href", "title"},
        "img": {"src", "alt", "title"},
        "th": {"colspan", "rowspan"},
        "td": {"colspan", "rowspan"},
    }

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.UNWRAP_TAGS or tag not in self.ALLOWED_TAGS:
            return
        allowed_attrs = self.ALLOWED_ATTRS.get(tag, set())
        attr_parts = []
        for key, value in attrs:
            if key not in allowed_attrs or value is None:
                continue
            attr_parts.append(f' {key}="{html.escape(value, quote=True)}"')
        if tag in self.VOID_TAGS:
            self.parts.append(f"<{tag}{''.join(attr_parts)} />")
            return
        self.parts.append(f"<{tag}{''.join(attr_parts)}>")

    def handle_endtag(self, tag):
        if tag in self.UNWRAP_TAGS or tag not in self.ALLOWED_TAGS or tag in self.VOID_TAGS:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(html.escape(data))

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        return

    def get_html(self):
        return "".join(self.parts)


def get_github_token():
    for env_name in ("GITHUB_TOKEN", "GH_TOKEN"):
        token = os.getenv(env_name)
        if token:
            return token
    combined_output = run_with_pty(["gh", "auth", "status", "--show-token"])
    match = re.search(r"Token:\s+(\S+)", combined_output)
    token = match.group(1) if match else ""
    if not token:
        raise RuntimeError("GitHub token is empty")
    return token


def run_with_pty(args):
    master_fd, slave_fd = pty.openpty()
    try:
        process = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=slave_fd,
            stderr=slave_fd,
            text=False,
        )
        os.close(slave_fd)
        chunks = []
        while True:
            try:
                chunk = os.read(master_fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            chunks.append(chunk)
        process.wait()
        return b"".join(chunks).decode("utf-8", errors="ignore")
    finally:
        try:
            os.close(master_fd)
        except OSError:
            pass


def fetch_posts(limit=None):
    posts = []
    next_page = ""
    session = requests.Session()
    while True:
        params = {
            "number": PAGE_SIZE,
            "fields": "ID,date,URL,slug,title,content,categories",
        }
        query = urllib.parse.urlencode(params)
        url = WORDPRESS_API + "?" + query
        if next_page:
            url += "&" + next_page
        response = session.get(url, timeout=30)
        response.raise_for_status()
        payload = response.json()
        posts.extend(payload["posts"])
        if limit and len(posts) >= limit:
            return posts[:limit]
        next_page = payload.get("meta", {}).get("next_page", "")
        if not next_page:
            return posts


def sanitize_html(raw_html):
    parser = HtmlSanitizer()
    parser.feed(raw_html or "")
    parser.close()
    sanitized = parser.get_html()
    sanitized = sanitized.replace("\r\n", "\n")
    while "\n\n\n" in sanitized:
        sanitized = sanitized.replace("\n\n\n", "\n\n")
    return sanitized.strip()


def normalize_categories(post):
    categories = list((post.get("categories") or {}).keys())
    return categories or ["未分类"]


def build_issue_body(post):
    published = post["date"]
    source_url = post["URL"]
    content = sanitize_html(post.get("content", ""))
    metadata = [
        "<!-- BLOG_POST -->",
        f"<!-- BLOG_PUBLISHED: {published} -->",
        f"<!-- BLOG_SOURCE_URL: {source_url} -->",
        f"<!-- BLOG_SOURCE: {MIGRATION_SOURCE} -->",
        "",
        f"> Migrated from `{MIGRATION_SOURCE}`.",
        f"> Originally published: `{published[:10]}`.",
        f"> Original URL: {source_url}",
        "",
    ]
    body = "\n".join(metadata) + content + "\n"
    if len(body) > MAX_ISSUE_BODY_LENGTH:
        raise ValueError(
            f"Issue body too large for '{post['title']}' ({len(body)} chars)"
        )
    return body


def extract_existing_source_urls(repo, me):
    existing = {}
    for issue in blog_main.get_blog_issues(repo, me):
        source_url = blog_main.get_issue_source_url(issue)
        if source_url:
            existing[source_url] = issue
    return existing


def pick_label_color(name):
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    return digest[:6]


def ensure_label(repo, existing_labels, name, description=""):
    if name in existing_labels:
        return existing_labels[name]
    try:
        label = repo.get_label(name)
    except UnknownObjectException:
        label = repo.create_label(
            name=name,
            color=pick_label_color(name),
            description=description,
        )
    existing_labels[name] = label
    return label


def create_or_skip_posts(repo, me, posts, close_created=True, dry_run=False):
    existing_source_urls = extract_existing_source_urls(repo, me)
    existing_labels = {label.name: label for label in repo.get_labels()}
    created = []
    skipped = []
    for post in sorted(posts, key=lambda item: item["date"]):
        source_url = post["URL"]
        if source_url in existing_source_urls:
            skipped.append((post["title"], "already migrated"))
            continue

        category_names = normalize_categories(post)
        if dry_run:
            created.append((post["title"], category_names))
            continue

        labels = [
            ensure_label(repo, existing_labels, BLOG_LABEL, "Blog posts"),
        ]
        for category_name in category_names:
            labels.append(ensure_label(repo, existing_labels, category_name))

        issue = repo.create_issue(
            title=post["title"],
            body=build_issue_body(post),
            labels=labels,
        )
        if close_created:
            issue.edit(state="closed")
        created.append((issue.number, post["title"]))
    return created, skipped


def refresh_generated_files(token, repo_name):
    blog_main.main(token, repo_name)


def print_summary(posts):
    bodies = [build_issue_body(post) for post in posts]
    max_length = max(len(body) for body in bodies) if bodies else 0
    print(f"posts={len(posts)}")
    print(f"max_issue_body_length={max_length}")
    print("latest_posts:")
    for post in sorted(posts, key=lambda item: item["date"], reverse=True)[:5]:
        print(f"- {post['date'][:10]} {post['title']}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_name", help="repo name, for example pacoxu/pacoxu")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="only migrate the first N posts ordered by publish time",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be created without creating issues",
    )
    parser.add_argument(
        "--keep-open",
        action="store_true",
        help="keep migrated issues open",
    )
    parser.add_argument(
        "--skip-refresh",
        action="store_true",
        help="skip regenerating README, feed.xml, and BACKUP",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="only print import statistics",
    )
    parser.add_argument(
        "--refresh-only",
        action="store_true",
        help="only regenerate README, feed.xml, and BACKUP from existing blog issues",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.refresh_only:
        token = get_github_token()
        refresh_generated_files(token, args.repo_name)
        print("refreshed=1")
        return

    posts = fetch_posts(limit=args.limit)
    if args.summary_only:
        print_summary(posts)
        return

    token = get_github_token()
    github = Github(token)
    repo = github.get_repo(args.repo_name)
    me = blog_main.get_me(github)

    created, skipped = create_or_skip_posts(
        repo=repo,
        me=me,
        posts=posts,
        close_created=not args.keep_open,
        dry_run=args.dry_run,
    )
    print(f"created={len(created)}")
    print(f"skipped={len(skipped)}")

    if args.dry_run:
        for title, categories in created[:10]:
            print(f"would_create={title} labels={','.join([BLOG_LABEL] + categories)}")
        return

    if created and not args.skip_refresh:
        refresh_generated_files(token, args.repo_name)

    for item in created[:10]:
        issue_number, title = item
        print(f"created_issue=#{issue_number} title={title}")


if __name__ == "__main__":
    try:
        main()
    except (GithubException, RuntimeError, ValueError, urllib.error.URLError) as exc:
        print(str(exc), file=sys.stderr)
        raise
