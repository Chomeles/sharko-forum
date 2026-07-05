"""Tiny BBCode + light-Markdown renderer. stdlib only, no Django template dep, so
it is unit-testable standalone:  python -m forum.bbcode

Security: the input is html.escape()d FIRST, then a fixed tag set is applied — user
text can never inject raw HTML, and link/img schemes are restricted to http(s)/relative.
ponytail: single-pass regex, no nesting of same-name tags, no code-block isolation
(formatting still applies inside [code]); good enough for forum posts.
"""
import html
import re

_URL_OK = re.compile(r"^(https?://|/)", re.I)  # reject javascript:, data:, etc.


def _link(url, text):
    u = html.unescape(url).strip()
    if not _URL_OK.match(u):
        return html.escape(html.unescape(text))  # bad scheme → show as plain text
    return f'<a href="{html.escape(u)}" rel="nofollow noopener" target="_blank">{text}</a>'


def _img(url):
    u = html.unescape(url).strip()
    if not _URL_OK.match(u):
        return html.escape(url)
    return f'<img src="{html.escape(u)}" alt="" loading="lazy" class="post-img">'


_HIDDEN = ('<div class="hidden-content">🔒 Hidden content — '
           'reply to the thread to reveal it.</div>')


def render(text, unlocked=False):
    s = html.escape(text or "")

    s = re.sub(r"\[code\](.+?)\[/code\]", lambda m: f"<pre><code>{m.group(1)}</code></pre>",
               s, flags=re.S | re.I)
    s = re.sub(r"`([^`\n]+?)`", lambda m: f"<code>{m.group(1)}</code>", s)

    s = re.sub(r"\[quote=([^\]\n]{1,60})\](.+?)\[/quote\]",
               lambda m: f"<blockquote><cite>{m.group(1).strip()} wrote:</cite>{m.group(2)}</blockquote>",
               s, flags=re.S | re.I)
    s = re.sub(r"\[quote\](.+?)\[/quote\]", lambda m: f"<blockquote>{m.group(1)}</blockquote>",
               s, flags=re.S | re.I)

    s = re.sub(r"\[hide\](.+?)\[/hide\]",
               lambda m: m.group(1) if unlocked else _HIDDEN, s, flags=re.S | re.I)

    s = re.sub(r"\[img\]([^\[\s]+?)\[/img\]", lambda m: _img(m.group(1)), s, flags=re.I)

    s = re.sub(r"\[url=([^\]\s]+?)\](.+?)\[/url\]", lambda m: _link(m.group(1), m.group(2)),
               s, flags=re.S | re.I)
    s = re.sub(r"\[url\]([^\[\s]+?)\[/url\]", lambda m: _link(m.group(1), m.group(1)), s, flags=re.I)
    s = re.sub(r"\[([^\]\n]+?)\]\(([^)\s]+?)\)", lambda m: _link(m.group(2), m.group(1)), s)

    s = re.sub(r"\[b\](.+?)\[/b\]", r"<strong>\1</strong>", s, flags=re.S | re.I)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s, flags=re.S)
    s = re.sub(r"\[i\](.+?)\[/i\]", r"<em>\1</em>", s, flags=re.S | re.I)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s, flags=re.S)
    s = re.sub(r"\[u\](.+?)\[/u\]", r"<u>\1</u>", s, flags=re.S | re.I)
    s = re.sub(r"\[s\](.+?)\[/s\]", r"<s>\1</s>", s, flags=re.S | re.I)

    return s.replace("\n", "<br>")


if __name__ == "__main__":
    assert render("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert render("[b]hi[/b]") == "<strong>hi</strong>"
    assert "javascript" not in render("[url=javascript:alert(1)]x[/url]")
    assert render("[url=javascript:alert(1)]x[/url]") == "x"
    assert 'hidden-content' in render("[hide]secret[/hide]")
    r = render("[hide]secret[/hide]", unlocked=True)
    assert "secret" in r and "hidden-content" not in r
    assert '<a href="https://x.com"' in render("[url]https://x.com[/url]")
    assert "<blockquote><cite>Al wrote:" in render("[quote=Al]hey[/quote]")
    assert render("a\nb") == "a<br>b"
    assert render("[link](https://ok.io)") == '<a href="https://ok.io" rel="nofollow noopener" target="_blank">link</a>'
    print("ok")
