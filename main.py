# -*- coding: utf-8 -*-
import argparse
import os
import re
from datetime import datetime, timezone

import markdown
from feedgen.feed import FeedGenerator
from github import Github
from lxml.etree import CDATA
from marko.ext.gfm import gfm as marko

BACKUP_DIR = "BACKUP"
README_FILE = "README.md"
BLOG_LIST_FILE = "blog-list.md"
README_TEMPLATE_FILE = "README_TEMPLATE.md"
BLOG_LIST_TEMPLATE_FILE = "BLOG_LIST_TEMPLATE.md"
BLOG_LIST_APPENDIX_FILE = "BLOG_LIST_APPENDIX.md"
ANCHOR_NUMBER = 5
BLOG_LABELS = ["Blog"]
TOP_ISSUES_LABELS = ["Top"]
TODO_ISSUES_LABELS = ["TODO"]
FRIENDS_LABELS = ["Friends"]
ABOUT_LABELS = ["About"]
THINGS_LABELS = ["Things"]
BLOG_PUBLISHED_PATTERN = re.compile(
    r"<!--\s*BLOG_PUBLISHED:\s*(?P<value>.*?)\s*-->", re.IGNORECASE
)
BLOG_SOURCE_URL_PATTERN = re.compile(
    r"<!--\s*BLOG_SOURCE_URL:\s*(?P<value>.*?)\s*-->", re.IGNORECASE
)
IGNORE_LABELS = (
    BLOG_LABELS
    + FRIENDS_LABELS
    + TOP_ISSUES_LABELS
    + TODO_ISSUES_LABELS
    + ABOUT_LABELS
    + THINGS_LABELS
)

FRIENDS_TABLE_HEAD = "| Name | Link | Desc | \n | ---- | ---- | ---- |\n"
FRIENDS_TABLE_TEMPLATE = "| {name} | {link} | {desc} |\n"
FRIENDS_INFO_DICT = {
    "名字": "",
    "链接": "",
    "描述": "",
}


def get_me(user):
    return user.get_user().login


def is_me(issue, me):
    return issue.user.login == me


def is_hearted_by_me(comment, me):
    reactions = list(comment.get_reactions())
    for r in reactions:
        if r.content == "heart" and r.user.login == me:
            return True
    return False


def _make_friend_table_string(s):
    info_dict = FRIENDS_INFO_DICT.copy()
    try:
        string_list = s.splitlines()
        # drop empty line
        string_list = [l for l in string_list if l and not l.isspace()]
        for l in string_list:
            string_info_list = re.split("：", l)
            if len(string_info_list) < 2:
                continue
            info_dict[string_info_list[0]] = string_info_list[1]
        return FRIENDS_TABLE_TEMPLATE.format(
            name=info_dict["名字"], link=info_dict["链接"], desc=info_dict["描述"]
        )
    except Exception as e:
        print(str(e))
        return


# help to covert xml vaild string
def _valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF
        or codepoint in (0x9, 0xA, 0xD)
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def format_time(time):
    return str(time)[:10]


def parse_blog_metadata(body):
    body = body or ""
    published_match = BLOG_PUBLISHED_PATTERN.search(body)
    source_url_match = BLOG_SOURCE_URL_PATTERN.search(body)
    return {
        "published": published_match.group("value") if published_match else "",
        "source_url": source_url_match.group("value") if source_url_match else "",
    }


def get_issue_published_at(issue):
    metadata = parse_blog_metadata(issue.body)
    published = metadata["published"]
    if published:
        try:
            return datetime.fromisoformat(published)
        except ValueError:
            pass
    created_at = issue.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at


def get_issue_source_url(issue):
    return parse_blog_metadata(issue.body)["source_url"]


def get_issue_display_time(issue):
    return format_time(get_issue_published_at(issue).date())


def is_blog_issue(issue, me):
    if issue.pull_request or not is_me(issue, me):
        return False
    label_names = {label.name for label in issue.labels}
    return BLOG_LABELS[0] in label_names


def sort_issues_by_published_at_desc(issues):
    return sorted(
        issues,
        key=lambda issue: (get_issue_published_at(issue), issue.number),
        reverse=True,
    )


def login(token):
    return Github(token)


def get_repo(user: Github, repo: str):
    return user.get_repo(repo)


def parse_TODO(issue):
    body = issue.body.splitlines()
    todo_undone = [l for l in body if l.startswith("- [ ] ")]
    todo_done = [l for l in body if l.startswith("- [x] ")]
    # just add info all done
    if not todo_undone:
        return f"[{issue.title}]({issue.html_url}) all done", []
    return (
        f"[{issue.title}]({issue.html_url})--{len(todo_undone)} jobs to do--{len(todo_done)} jobs done",
        todo_done + todo_undone,
    )


def get_top_issues(repo):
    return repo.get_issues(labels=TOP_ISSUES_LABELS, state="all")


def get_todo_issues(repo):
    return repo.get_issues(labels=TODO_ISSUES_LABELS)


def get_repo_labels(repo):
    return [l for l in repo.get_labels()]


def get_issues_from_label(repo, label, state="open"):
    return repo.get_issues(labels=(label,), state=state)


def get_blog_issues(repo, me, state="all"):
    issues = get_issues_from_label(repo, BLOG_LABELS[0], state=state)
    return sort_issues_by_published_at_desc(
        [issue for issue in issues if is_blog_issue(issue, me)]
    )


def add_issue_info(issue, md):
    time = get_issue_display_time(issue)
    md.write(f"- [{issue.title}]({issue.html_url})--{time}\n")


def add_md_todo(repo, md, me):
    todo_issues = list(get_todo_issues(repo))
    if not TODO_ISSUES_LABELS or not todo_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## TODO\n")
        for issue in todo_issues:
            if is_me(issue, me):
                todo_title, todo_list = parse_TODO(issue)
                md.write("TODO list from " + todo_title + "\n")
                for t in todo_list:
                    md.write(t + "\n")
                # new line
                md.write("\n")


def add_md_top(repo, md, me):
    top_issues = [
        issue for issue in list(get_top_issues(repo)) if is_blog_issue(issue, me)
    ]
    if not TOP_ISSUES_LABELS or not top_issues:
        return
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## 置顶文章\n")
        for issue in sort_issues_by_published_at_desc(top_issues):
            add_issue_info(issue, md)


def add_md_friends(repo, md, me):
    friends_issues = list(get_issues_from_label(repo, FRIENDS_LABELS[0]))
    if not FRIENDS_LABELS or not friends_issues:
        return
    friends_issue_number = friends_issues[0].number
    s = FRIENDS_TABLE_HEAD
    for issue in friends_issues:
        if is_me(issue, me):
            s += _make_friend_table_string(issue.body or "")
            for comment in issue.get_comments():
                if is_me(comment, me) or is_hearted_by_me(comment, me):
                    try:
                        s += _make_friend_table_string(comment.body or "")
                    except Exception as e:
                        print(str(e))
                        pass
    s = markdown.markdown(s, output_format="html", extensions=["extra"])
    with open(md, "a+", encoding="utf-8") as md:
        md.write(
            f"## [友情链接](https://github.com/{repo.full_name}/issues/{friends_issue_number})\n"
        )
        md.write("<details><summary>显示</summary>\n")
        md.write(s)
        md.write("</details>\n")
        md.write("\n\n")


def add_md_recent(repo, md, me, limit=5):
    count = 0
    with open(md, "a+", encoding="utf-8") as md:
        md.write("## 最近更新\n")
        for issue in get_blog_issues(repo, me)[:limit]:
            add_issue_info(issue, md)
            count += 1
            if count >= limit:
                break


def write_md_from_template(md, repo_name, template_file, fallback):
    if os.path.exists(template_file):
        with open(template_file, "r", encoding="utf-8") as f:
            header = f.read()
        with open(md, "w", encoding="utf-8") as out:
            out.write(header.format(repo_name=repo_name))
            out.write("\n")
    else:
        with open(md, "w", encoding="utf-8") as out:
            out.write(fallback.format(repo_name=repo_name))
            out.write("\n")


def append_markdown_file(md, source_file):
    if not os.path.exists(source_file):
        return
    with open(source_file, "r", encoding="utf-8") as source:
        content = source.read().strip()
    if not content:
        return
    with open(md, "a+", encoding="utf-8") as out:
        out.write("\n")
        out.write(content)
        out.write("\n")


def add_md_label(repo, md, me):
    labels = get_repo_labels(repo)

    # sort labels by description info if it exists, otherwise sort by name,
    # for example, we can let the description start with a number (1#Java, 2#Docker, 3#K8s, etc.)
    labels = sorted(
        labels,
        key=lambda x: (
            x.description is None,
            x.description == "",
            x.description,
            x.name,
        ),
    )

    with open(md, "a+", encoding="utf-8") as md:
        for label in labels:
            # we don't need add top label again
            if label.name in IGNORE_LABELS:
                continue

            issues = get_issues_from_label(repo, label, state="all")
            issues = sort_issues_by_published_at_desc(
                [issue for issue in issues if is_blog_issue(issue, me)]
            )
            if len(issues) != 0:
                md.write("## " + label.name + "\n\n")
            i = 0
            for issue in issues:
                if i == ANCHOR_NUMBER:
                    md.write("<details><summary>显示更多</summary>\n")
                    md.write("\n")
                add_issue_info(issue, md)
                i += 1
            if i > ANCHOR_NUMBER:
                md.write("</details>\n")
                md.write("\n")


def get_to_generate_issues(repo, dir_name, issue_number=None):
    md_files = os.listdir(dir_name)
    generated_issues_numbers = [
        int(i.split("_")[0]) for i in md_files if i.split("_")[0].isdigit()
    ]
    to_generate_issues = [
        i
        for i in list(repo.get_issues(labels=BLOG_LABELS, state="all"))
        if int(i.number) not in generated_issues_numbers
    ]
    if issue_number:
        to_generate_issues.append(repo.get_issue(int(issue_number)))
    return sort_issues_by_published_at_desc(to_generate_issues)


def generate_rss_feed(repo, filename, me):
    generator = FeedGenerator()
    generator.id(repo.html_url)
    generator.title(f"RSS feed of {repo.owner.login}'s {repo.name}")
    generator.author(
        {"name": os.getenv("GITHUB_NAME", me), "email": os.getenv("GITHUB_EMAIL", "")}
    )
    generator.link(href=repo.html_url)
    generator.link(
        href=f"https://raw.githubusercontent.com/{repo.full_name}/master/{filename}",
        rel="self",
    )
    for issue in reversed(get_blog_issues(repo, me)):
        if not issue.body:
            continue
        item = generator.add_entry(order="append")
        item.id(issue.html_url)
        item.link(href=issue.html_url)
        item.title(issue.title)
        item.published(get_issue_published_at(issue).isoformat())
        for label in issue.labels:
            if label.name == BLOG_LABELS[0]:
                continue
            item.category({"term": label.name})
        body = "".join(c for c in issue.body if _valid_xml_char_ordinal(c))
        item.content(CDATA(marko.convert(body)), type="html")
    generator.atom_file(filename)


def generate_profile_readme(repo_name):
    write_md_from_template(
        README_FILE,
        repo_name,
        README_TEMPLATE_FILE,
        (
            "## My Blog\n\n"
            "The full archive lives in [blog-list.md](https://github.com/{repo_name}/blob/master/blog-list.md).\n\n"
            "[RSS Feed](https://raw.githubusercontent.com/{repo_name}/master/feed.xml)\n"
        ),
    )


def generate_blog_list(repo, repo_name, me):
    write_md_from_template(
        BLOG_LIST_FILE,
        repo_name,
        BLOG_LIST_TEMPLATE_FILE,
        (
            "# My Blog\n\n"
            "The full archive lives here so the profile README can stay focused.\n\n"
            "- [Back to profile](https://github.com/{repo_name})\n"
            "- [RSS Feed](https://raw.githubusercontent.com/{repo_name}/master/feed.xml)\n"
            "- [GitHub Issues](https://github.com/{repo_name}/issues)\n\n"
            "Blog posts are managed via GitHub Issues. Create a new issue with the `Blog` label to publish a blog post.\n"
        ),
    )
    for func in [add_md_top, add_md_recent, add_md_label]:
        func(repo, BLOG_LIST_FILE, me)
    append_markdown_file(BLOG_LIST_FILE, BLOG_LIST_APPENDIX_FILE)


def main(token, repo_name, issue_number=None, dir_name=BACKUP_DIR):
    user = login(token)
    me = get_me(user)
    repo = get_repo(user, repo_name)
    generate_profile_readme(repo_name)
    generate_blog_list(repo, repo_name, me)

    generate_rss_feed(repo, "feed.xml", me)
    to_generate_issues = get_to_generate_issues(repo, dir_name, issue_number)

    # save md files to backup folder
    for issue in to_generate_issues:
        save_issue(issue, me, dir_name)


def save_issue(issue, me, dir_name=BACKUP_DIR):
    md_name = os.path.join(
        dir_name, f"{issue.number}_{issue.title.replace('/', '-').replace(' ', '.')}.md"
    )
    with open(md_name, "w") as f:
        f.write(f"# [{issue.title}]({issue.html_url})\n\n")
        f.write(issue.body or "")
        if issue.comments:
            for c in issue.get_comments():
                if is_me(c, me):
                    f.write("\n\n---\n\n")
                    f.write(c.body or "")


if __name__ == "__main__":
    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument(
        "--issue_number", help="issue_number", default=None, required=False
    )
    options = parser.parse_args()
    main(options.github_token, options.repo_name, options.issue_number)
