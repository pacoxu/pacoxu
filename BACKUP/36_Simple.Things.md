# [Simple Things](https://github.com/pacoxu/pacoxu/issues/36)

<!-- BLOG_POST -->
<!-- BLOG_PUBLISHED: 2016-08-03T14:23:50+08:00 -->
<!-- BLOG_SOURCE_URL: https://pacoxu.wordpress.com/2016/08/03/simple-words/ -->
<!-- BLOG_SOURCE: pacoxu.wordpress.com -->

> Migrated from `pacoxu.wordpress.com`.
> Originally published: `2016-08-03`.
> Original URL: https://pacoxu.wordpress.com/2016/08/03/simple-words/
<h1>Definition</h1>
<p>Radix: 16/10/8/2</p>
<blockquote><p>In mathematical numeral systems, the radix or base is the number of unique digits,</p>
<p>From wikipedia</p>
</blockquote>
<h1>Python</h1>
<h2>URL Route Registrations</h2>
<p>Generally there are three ways to define rules for the routing system:</p>
<ol>
<li>You can use the <a title="flask.Flask.route" href="http://flask.pocoo.org/docs/0.11/api/#flask.Flask.route"><code>flask.Flask.route()</code></a> decorator.</li>
<li>You can use the <a title="flask.Flask.add_url_rule" href="http://flask.pocoo.org/docs/0.11/api/#flask.Flask.add_url_rule"><code>flask.Flask.add_url_rule()</code></a> function.</li>
<li>You can directly access the underlying Werkzeug routing system which is exposed as <a title="flask.Flask.url_map" href="http://flask.pocoo.org/docs/0.11/api/#flask.Flask.url_map"><code>flask.Flask.url_map</code></a>.</li>
</ol>
<h1>Linux</h1>
<h2>Find Largest/Biggest files in linux system</h2>
<h3>Top 10 largest files:</h3>
<p>du -cks * | sort -rn | head</p>
<h3>Big files larger than 50MB</h3>
<p>$ find . -type f -size +50000k -exec ls -lh {} \; | awk &#8216;{ print $9 &#8220;: &#8221; $5 }&#8217;</p>
<h3>Alias</h3>
<p>alias gp=&#8217;git pull&#8217;</p>
<h2>Reference:</h2>
<p><a href="http://www.cyberciti.biz/faq/how-do-i-find-the-largest-filesdirectories-on-a-linuxunixbsd-filesystem/">http://www.cyberciti.biz/faq/how-do-i-find-the-largest-filesdirectories-on-a-linuxunixbsd-filesystem/</a></p>
<p><a href="http://www.cyberciti.biz/faq/find-large-files-linux/">http://www.cyberciti.biz/faq/find-large-files-linux/</a></p>
<pre><code>add-apt-repository
</code></pre>
<pre><code>depends on
apt-get install software-properties-common
</code></pre>
<pre><code></code>nginx 1.10.1 对应 openssl 1.0.1e 不支持http2
openssl 1.0.2d开始支持http2
nginx则需要 1.11.3

grep -Erin &#x27;&#x27; ./</pre>
