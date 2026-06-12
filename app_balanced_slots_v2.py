import os
import argparse
import subprocess
import random
from dotenv import load_dotenv
import json
from datetime import datetime
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing

# Load environment variables from .env file
load_dotenv()


def flatten_tif_to_image_in_memory(tif_file):
    """
    Flattens a TIF file and loads it into an in-memory Wand image using ImageMagick.

    Args:
        tif_file (str): Path to the TIF file.

    Returns:
        Image: Wand image object of the flattened and processed TIF.
    """
    try:
        # Use env override first, then fallback to common Windows ImageMagick path.
        magick_path = os.environ.get(
            "MAGICK_PATH",
            r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
        )

        command = [
            magick_path,
            "convert",
            tif_file,
            "-quiet",
            "-background", "none",
            "-flatten",
            "-transparent", "white",
            "PNG:-"
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        img = Image(blob=result.stdout)
        img.trim()
        return img

    except subprocess.CalledProcessError as e:
        print(f"Error processing TIF: {tif_file} - {e.stderr.decode('utf-8')}")
        return None


def safe_slug(value):
    """
    Creates a simple filename-safe slug.
    """
    return (
        value.lower()
        .replace("'", "")
        .replace("&", "and")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(" ", "-")
    )


def get_balanced_slots(item_count):
    """
    Slot-based layout to replace random/scattered placement.

    Why:
    - Keeps products fully inside the canvas.
    - Reduces uneven left/right weight.
    - Avoids partially cropped far-right items.
    - Creates predictable ecommerce/email banner composition.

    Slot values:
    - x_pct: horizontal center position as percentage of canvas width.
    - y_pct: top position as percentage of product area height.
    - size: target max box size for product image.
    """

    if item_count <= 1:
        return [
            {"x_pct": 0.50, "y_pct": 0.12, "size": 310},
        ]

    if item_count == 2:
        return [
            {"x_pct": 0.34, "y_pct": 0.14, "size": 250},
            {"x_pct": 0.66, "y_pct": 0.18, "size": 235},
        ]

    if item_count == 3:
        return [
            {"x_pct": 0.25, "y_pct": 0.14, "size": 230},
            {"x_pct": 0.50, "y_pct": 0.18, "size": 215},
            {"x_pct": 0.75, "y_pct": 0.16, "size": 205},
        ]

    if item_count == 4:
        return [
            {"x_pct": 0.20, "y_pct": 0.11, "size": 220},  # left item
            {"x_pct": 0.43, "y_pct": 0.20, "size": 185},  # center item
            {"x_pct": 0.66, "y_pct": 0.16, "size": 165},  # right-center item
            {"x_pct": 0.84, "y_pct": 0.23, "size": 160},  # far-right item, kept inside
        ]

    if item_count == 5:
        # Wider, cleaner 5-item layout.
        # Designed for mixed sports products where one item may be a tall package/box.
        # Reduces center crowding and keeps the far-right item fully inside the banner.
        return [
            {"x_pct": 0.14, "y_pct": 0.18, "size": 150},  # far-left small/box item
            {"x_pct": 0.28, "y_pct": 0.32, "size": 135},  # lower-left ball/small item
            {"x_pct": 0.50, "y_pct": 0.07, "size": 205},  # center hero item
            {"x_pct": 0.70, "y_pct": 0.22, "size": 155},  # right-center support item
            {"x_pct": 0.86, "y_pct": 0.13, "size": 175},  # far-right item
        ]

    # 6+ items: stable grid-like distribution with slight stagger.
    return [
        {"x_pct": 0.14, "y_pct": 0.11, "size": 165},
        {"x_pct": 0.31, "y_pct": 0.20, "size": 155},
        {"x_pct": 0.48, "y_pct": 0.10, "size": 165},
        {"x_pct": 0.65, "y_pct": 0.21, "size": 155},
        {"x_pct": 0.82, "y_pct": 0.12, "size": 155},
        {"x_pct": 0.50, "y_pct": 0.32, "size": 145},
    ]


def composite_product_in_slot(canvas, img, slot, available_height, enable_micro_variation=True):
    """
    Resize and place product image into a fixed slot while preventing cropping.
    """

    item_size = slot["size"]
    img.transform(resize=f"{item_size}x{item_size}>")

    x = int(canvas.width * slot["x_pct"] - img.width / 2)
    y = int(available_height * slot["y_pct"])

    # Optional tiny variation to avoid a mechanical look.
    # This is intentionally small. Main layout is not random.
    if enable_micro_variation:
        x += random.randint(-4, 4)
        y += random.randint(-3, 3)

    safe_margin = 20

    # Prevent any image from being cut off by canvas edges or caption area.
    x = max(safe_margin, min(x, canvas.width - img.width - safe_margin))
    y = max(safe_margin, min(y, available_height - img.height - safe_margin))

    canvas.composite(img, left=x, top=y)
    return x, y, img.width, img.height


def draw_caption(canvas, caption, caption_color):
    """
    Adds centered caption text at the bottom. Splits into two lines if needed.
    """

    max_caption_width = canvas.width - 40

    with Drawing() as draw:
        draw.font = "Arial-Bold"
        draw.font_size = 45
        draw.fill_color = Color(caption_color)
        draw.text_alignment = "center"

        words = caption.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if draw.get_font_metrics(canvas, test_line).text_width <= max_caption_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        if len(lines) == 1:
            caption_y = canvas.height - 60
            draw.text(canvas.width // 2, caption_y, lines[0])
        else:
            # Limit to 2 lines visually. Merge overflow into the second line.
            if len(lines) > 2:
                lines = [lines[0], " ".join(lines[1:])]

            caption_y = canvas.height - 78
            line_spacing = 44
            for line in lines:
                draw.text(canvas.width // 2, caption_y, line)
                caption_y += line_spacing

        draw(canvas)


def resolve_event_background(event_config: dict) -> str:
    """
    Resolve the configured event background path with a legacy bg.png fallback.
    """

    configured_background = event_config.get("background", "bg.png")
    background_path = os.path.join(os.getcwd(), configured_background)

    if os.path.exists(background_path):
        return background_path

    fallback_path = os.path.join(os.getcwd(), "bg.png")
    if os.path.exists(fallback_path):
        print(
            f"Warning: Background image '{configured_background}' not found. "
            "Using fallback 'bg.png'."
        )
        return fallback_path

    raise FileNotFoundError(
        f"Background image '{configured_background}' not found, and fallback 'bg.png' is missing."
    )


def create_banner(item_numbers, caption, event_code):
    """
    Creates a balanced category banner by placing flattened product images on bg.png,
    drawing a divider/spacer, adding a caption, and saving a WEBP output.

    Args:
        item_numbers (list): List of item numbers representing the TIF files.
        caption (str): Caption text to be added to the banner.
        event_code (str): 4-letter event code of the event for color scheme.
    """

    with open("events.json", "r") as f:
        events = json.load(f)

    if event_code not in events["events"]:
        raise ValueError(f"Invalid event code: {event_code}. Please check your events.json file.")

    # Keep original behavior from your script:
    # spacer_color comes from caption_color, caption_color comes from spacer_color.
    # If your events.json names are reversed, switch these two lines.
    event_config = events["events"][event_code]
    caption_color = event_config.get("spacer_color", "gray")
    spacer_color = event_config.get("caption_color", "black")

    event_full_name = safe_slug(event_config["full_name"])
    background_path = resolve_event_background(event_config)

    tiff_directory = os.environ.get("TIFF_DIRECTORY")
    if not tiff_directory:
        raise ValueError("TIFF_DIRECTORY is not set. Add it to your .env file.")

    with Image(filename=background_path) as canvas:
        # Reserve lower area for divider/spacer and caption.
        reserved_caption_height = 150
        available_height = canvas.height - reserved_caption_height

        # Draw horizontal spacer above the caption.
        spacer_y = canvas.height - reserved_caption_height
        with Drawing() as draw:
            draw.stroke_color = Color(spacer_color)
            draw.stroke_width = 8
            draw.line((0, spacer_y), (canvas.width, spacer_y))
            draw(canvas)

        slots = get_balanced_slots(len(item_numbers))
        placed_count = 0

        for idx, item_number in enumerate(item_numbers):
            tif_file = os.path.join(tiff_directory, f"{item_number}.tif")

            if not os.path.exists(tif_file):
                print(f"Warning: TIF file for item {item_number} not found. Skipping.")
                continue

            img = flatten_tif_to_image_in_memory(tif_file)
            if not img:
                continue

            # Use the next slot for each successfully loaded product.
            slot_index = placed_count % len(slots)
            slot = slots[slot_index]

            x, y, w, h = composite_product_in_slot(
                canvas=canvas,
                img=img,
                slot=slot,
                available_height=available_height,
                enable_micro_variation=True
            )

            placed_count += 1
            print(
                f"Item {idx + 1} ({item_number}): "
                f"Slot={slot_index + 1}, Size={w}x{h}, Position=({x}, {y})"
            )

            img.close()

        print(f"Balanced slot layout: {placed_count}/{len(item_numbers)} items placed")

        draw_caption(canvas, caption, caption_color)

        print(f"Canvas dimensions: {canvas.width}x{canvas.height}")

        caption_hyphenated = safe_slug(caption)
        timestamp = datetime.now().strftime("%m%d")
        output_filename = f"4sgm-{event_full_name}-wholesale-{caption_hyphenated}-{timestamp}.webp"
        output_path = os.path.join(os.getcwd(), output_filename)

        canvas.format = "webp"
        canvas.save(filename=output_path)

        print(f"Banner saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a balanced banner with product images.")
    parser.add_argument("item_numbers", nargs="+", help="Item numbers of the products, for example: 123456")
    parser.add_argument("-c", "--caption", required=True, help="Caption text for the banner")
    parser.add_argument("-e", "--event", required=True, help="4-letter event code, for example: MOMD, DADD")
    args = parser.parse_args()

    create_banner(args.item_numbers, args.caption, args.event)
