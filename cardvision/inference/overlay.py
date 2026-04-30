"""
Draw bounding boxes and card labels onto an image.
Returns a PIL Image with broadcast-style overlays.

Red labels for hearts/diamonds, dark labels for clubs/spades.
"""

from PIL import Image, ImageDraw, ImageFont

# Suit color map: red for hearts/diamonds, near-black for clubs/spades
_SUIT_COLORS = {
    "h": "#e03030",
    "d": "#e03030",
    "c": "#1a1a1a",
    "s": "#1a1a1a",
}
_BOX_ALPHA = 180   # bounding box border opacity (0-255)
_LABEL_BG_ALPHA = 200


def _suit_color(class_name: str) -> str:
    suit = class_name[-1].lower() if class_name else "s"
    return _SUIT_COLORS.get(suit, "#1a1a1a")


def _friendly_name(class_name: str) -> str:
    rank_map = {"T": "10", "J": "Jack", "Q": "Queen", "K": "King", "A": "Ace"}
    suit_map = {"c": "Clubs", "d": "Diamonds", "h": "Hearts", "s": "Spades"}
    rank = class_name[:-1]
    suit = class_name[-1]
    return f"{rank_map.get(rank, rank)} of {suit_map.get(suit, suit)}"


def draw_overlay(image_path: str, detections: list[dict]) -> Image.Image:
    img = Image.open(image_path).convert("RGB")
    if not detections:
        return img

    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=22)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=16)
    except OSError:
        font = ImageFont.load_default()
        small_font = font

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cls = det["class"]
        conf = det["confidence"]
        color_hex = _suit_color(cls)

        # Bounding box
        r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
        draw.rectangle([x1, y1, x2, y2], outline=(r, g, b, _BOX_ALPHA), width=3)

        # Label background
        label = f"{cls}  {conf:.0%}"
        bbox_text = draw.textbbox((x1, y1 - 28), label, font=font)
        draw.rectangle(
            [bbox_text[0] - 4, bbox_text[1] - 2, bbox_text[2] + 4, bbox_text[3] + 2],
            fill=(r, g, b, _LABEL_BG_ALPHA),
        )
        draw.text((x1, y1 - 28), label, fill="white", font=font)

    return img


def card_list_text(detections: list[dict]) -> str:
    if not detections:
        return "No cards detected"
    return "  ·  ".join(_friendly_name(d["class"]) for d in detections)
