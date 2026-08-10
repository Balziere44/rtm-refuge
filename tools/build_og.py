# -*- coding: utf-8 -*-
"""Draw the social share card.

    python tools/build_og.py

This is the picture Discord, Slack and every chat client show when somebody
pastes the link, so it is often the first thing anyone sees of the project.
It used to be a hand-made JPEG with no source, which meant changing one line
of it was a graphics-editor job. Now it is generated like everything else.

1200x630 is the size every platform crops from. The mark sits left with a
purple field behind it, the wordmark and one sentence sit right, and a short
strip of three claims runs under a rule.
"""

import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MARK = os.path.join(ROOT, "assets", "img", "mark-900.png")
OUT = os.path.join(ROOT, "assets", "social", "og-cover.jpg")

W, H = 1200, 630

# The one place the card's words live.
TITLE_TOP = "RETURN TO MORROC"
TITLE_BOT = "REFUGE"
LEDE = ["A custom classic-fantasy MMO world,",
        "rebuilt from the ashes by its own players."]
# Three claims, in the order they matter. Nothing here may be a number that
# goes stale, and nothing here may be a promise the project cannot keep.
STRIP = ["Brand New Classes", "New Items", "New Progression"]

INK = (245, 243, 250)
PURPLE = (169, 92, 255)
DIM = (176, 168, 190)
RULE = (138, 59, 200)

# Windows ships these and they are what the first card was set in. Falling
# back to Pillow's bitmap default would silently produce a card that looks
# nothing like the site, so a missing font is an error, not a warning.
FONTS = {
    "bold": r"C:\Windows\Fonts\segoeuib.ttf",
    "regular": r"C:\Windows\Fonts\segoeui.ttf",
}


def font(kind, size):
    path = FONTS[kind]
    if not os.path.exists(path):
        raise SystemExit("missing font: %s" % path)
    return ImageFont.truetype(path, size)


def radial(size, centre, radius, colour):
    """A soft round field of light, drawn small and scaled up.

    Drawing it at a sixteenth of the size and enlarging is both far faster
    than a per-pixel loop and smoother than one, because the resize does the
    interpolation.
    """
    w, h = size
    small = Image.new("L", (w // 8, h // 8), 0)
    d = ImageDraw.Draw(small)
    cx, cy, r = centre[0] // 8, centre[1] // 8, radius // 8
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        d.ellipse([cx - r * t, cy - r * t, cx + r * t, cy + r * t],
                  fill=int(255 * (1 - t) ** 2))
    small = small.filter(ImageFilter.GaussianBlur(6))
    mask = small.resize((w, h), Image.LANCZOS)
    field = Image.new("RGB", (w, h), colour)
    return field, mask


def background():
    im = Image.new("RGB", (W, H), (5, 3, 8))

    # The purple field behind the mark, and a wider dimmer one so the left
    # edge does not end in a hard circle.
    for centre, radius, colour in (
        ((235, 315), 620, (52, 9, 88)),
        ((205, 300), 340, (88, 21, 146)),
        ((110, 235), 195, (112, 36, 178)),
    ):
        field, mask = radial((W, H), centre, radius, colour)
        im = Image.composite(field, im, mask)

    return im


def place_mark(im):
    """The mark is on black, so screening it drops the black and keeps the
    glow. Compositing it any other way would paste a black square."""
    mark = Image.open(MARK).convert("RGB").resize((410, 410), Image.LANCZOS)
    plate = Image.new("RGB", (W, H), (0, 0, 0))
    plate.paste(mark, (50, 112))
    return ImageChops.screen(im, plate)


def draw_text(im):
    d = ImageDraw.Draw(im)
    x = 500

    d.text((x, 192), TITLE_TOP, font=font("bold", 58), fill=INK)
    d.text((x, 258), TITLE_BOT, font=font("bold", 58), fill=PURPLE)

    f = font("regular", 30)
    for i, line in enumerate(LEDE):
        d.text((x, 340 + i * 40), line, font=f, fill=INK)

    d.rectangle([x, 435, x + 118, 438], fill=RULE)

    f = font("regular", 25)
    cursor = x
    for i, claim in enumerate(STRIP):
        if i:
            d.text((cursor, 468), "|", font=f, fill=(96, 88, 110))
            cursor += d.textlength("|", font=f) + 18
        d.text((cursor, 468), claim, font=f, fill=DIM)
        cursor += d.textlength(claim, font=f) + 18
    return im


def main():
    im = draw_text(place_mark(background()))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    print("  wrote assets/social/og-cover.jpg - %d kb"
          % (os.path.getsize(OUT) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
