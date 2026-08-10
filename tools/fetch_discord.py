# -*- coding: utf-8 -*-
"""Parse the team's Discord exports into tools/data/discord.json.

    python tools/fetch_discord.py

The design decisions for the Refuge are announced in the project's own Discord
and nowhere else - there is no design document. The exports (DiscordChatExporter
HTML, saved by hand into "Refuge info discord" next to this repository) are
therefore the primary source for every "what the Refuge changed" claim on the
site, and this turns them into something the build and a reader can check.

The exporter writes its attributes unquoted (class=chatlog__content), so every
pattern here has to allow for that; matching only quoted values silently finds
nothing at all.

The output is committed, so the build never needs the exports present.
"""

import html as htmllib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(ROOT), "Refuge info discord")
OUT = os.path.join(HERE, "data", "discord.json")


def cls(name):
    """A class attribute the exporter may have written with or without quotes."""
    return r'class="?[^">]*\b%s\b[^">]*"?' % name


TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t]+")


def text_of(fragment):
    """Markup to text, keeping the line and list structure the author typed."""
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", fragment)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)<li[^>]*>", "\n- ", s)
    s = re.sub(r"(?i)</(p|div|ul|ol|li|h[1-6]|blockquote)>", "\n", s)
    s = TAG.sub("", s)
    s = htmllib.unescape(s)
    s = WS.sub(" ", s)
    s = "\n".join(line.strip() for line in s.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def messages(src):
    out = []
    author, stamp = "", ""
    # Messages in a group share one header, so author and time carry forward.
    for block in re.split(r"(?=<div [^>]*chatlog__message-container)", src)[1:]:
        m = re.search(cls("chatlog__author") + r"[^>]*>(.*?)</span>", block, re.S)
        if m:
            author = text_of(m.group(1))
        m = re.search(cls("chatlog__timestamp") + r"[^>]*>(.*?)</span>", block, re.S)
        if m:
            stamp = text_of(m.group(1)).strip("[]")

        body = []
        for pattern in ("chatlog__content", "chatlog__embed-title",
                        "chatlog__embed-description", "chatlog__embed-field-name",
                        "chatlog__embed-field-value"):
            for m in re.finditer(r"<div [^>]*" + cls(pattern) + r"[^>]*>(.*?)</div>",
                                 block, re.S):
                body.append(text_of(m.group(1)))

        blob = re.sub(r"\n{3,}", "\n\n", "\n".join(b for b in body if b)).strip()
        if blob:
            out.append({"author": author, "at": stamp, "text": blob})
    return out


def channel_of(filename):
    """The exporter writes "Server - channel - topic [id].html"."""
    stem = re.sub(r"\s*\[\d+\]\.html$", "", filename)
    parts = [p.strip() for p in stem.split(" - ")]
    return (parts[-2], parts[-1]) if len(parts) >= 3 else ("", parts[-1])


def main():
    if not os.path.isdir(SRC):
        print("no exports at %s" % SRC, file=sys.stderr)
        return 1

    threads = []
    for name in sorted(os.listdir(SRC)):
        if not name.lower().endswith(".html"):
            continue
        src = io.open(os.path.join(SRC, name), encoding="utf-8", errors="replace").read()
        msgs = messages(src)
        if not msgs:
            continue
        channel, topic = channel_of(name)
        threads.append({"channel": channel, "topic": topic, "messages": msgs})

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"threads": threads}, fh, ensure_ascii=False, indent=1,
                  sort_keys=True)
        fh.write("\n")

    total = sum(len(t["messages"]) for t in threads)
    words = sum(len(m["text"].split()) for t in threads for m in t["messages"])
    print("discord: %d threads, %d messages, %d words - %d kb"
          % (len(threads), total, words, os.path.getsize(OUT) // 1024))
    for t in threads:
        print("  %-22s %-50s %d msg" % (t["channel"][:22], t["topic"][:50],
                                        len(t["messages"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
