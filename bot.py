import os
import random
import logging
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

JOKES = [
    "Why did the Nigerian bring a fan to the interview? Because he heard the questions would be hot.",
    "NEPA is the only company that can turn off your Netflix, your fridge, and your generator dreams all at once.",
    "You know you're Nigerian when 'I'm coming' can mean anywhere from five minutes to five hours.",
    "Why don't Nigerian parents ever say 'I don't know'? Because somewhere, someone in the family knows a professor who knows.",
    "Danfo drivers should get a physics award for calculating exactly how many humans fit in a space built for twelve.",
    "In Nigeria, 'small chops' is never small and 'now now' is never now.",
    "Why did the jollof rice cross the party? Because it heard there was a competition next door.",
    "A Nigerian wedding has three timelines: the invitation time, the actual start time, and the time aunty finally stops dancing.",
    "Only in Nigeria will 'I'll call you back' become a permanent goodbye.",
    "Why did the phone charger become the most valuable item at the party? Because NEPA had other plans.",
    "You haven't experienced multitasking until you've seen a Nigerian mother pound yam while settling a phone call and supervising homework.",
    "Why do Nigerian keke drivers never need GPS? Because they already know every shortcut and every pothole by name.",
    "The real Nigerian superpower is turning 'we should hang out sometime' into a WhatsApp group that never meets.",
    "Why did the generator become the most respected member of the house? Because without it, nothing else works.",
    "In Nigeria, traffic isn't a delay, it's a whole social event with hawkers, sermons, and roadside snacks.",
]

MEME_COLORS = [
    "#1D9E75",  # jollof green
    "#D85A30",  # jollof orange
    "#378ADD",  # naija blue
    "#EF9F27",  # traffic amber
    "#2C2C2A",  # NEPA black
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int):
    words = text.upper().split()
    lines = []
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and line:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines


def draw_centered_lines(draw, lines, font, cx, top_y, line_height, fill="white", outline="black"):
    y = top_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = cx - w / 2
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                draw.text((x + dx, y + dy), line, font=font, fill=outline)
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def make_meme(top_text: str, bottom_text: str) -> BytesIO:
    size = 600
    img = Image.new("RGB", (size, size), color=random.choice(MEME_COLORS))
    draw = ImageDraw.Draw(img)
    font = get_font(42)

    max_w = size - 60
    line_h = 50

    top_lines = wrap_text(draw, top_text, font, max_w)
    bottom_lines = wrap_text(draw, bottom_text, font, max_w)

    draw_centered_lines(draw, top_lines, font, size / 2, 30, line_h)

    bottom_block_h = len(bottom_lines) * line_h
    start_y = size - 30 - bottom_block_h
    draw_centered_lines(draw, bottom_lines, font, size / 2, start_y, line_h)

    buf = BytesIO()
    buf.name = "meme.png"
    img.save(buf, "PNG")
    buf.seek(0)
    return buf


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Wetin dey happen! 👋\n\n"
        "/joke - random Nigerian joke\n"
        "/meme - random meme picture\n"
        "/meme <top text> | <bottom text> - custom meme"
    )


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(JOKES))


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args_text = " ".join(context.args) if context.args else ""
    if "|" in args_text:
        top, bottom = [s.strip() for s in args_text.split("|", 1)]
    elif args_text:
        top, bottom = args_text, ""
    else:
        j = random.choice(JOKES)
        mid = len(j) // 2
        split_at = j.find(" ", mid)
        if split_at == -1:
            split_at = mid
        top, bottom = j[:split_at].strip(), j[split_at:].strip()

    buf = make_meme(top, bottom)
    await update.message.reply_photo(photo=buf)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("meme", meme))

    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
