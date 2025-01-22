import os
import argparse
import subprocess
from io import BytesIO
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from dotenv import load_dotenv
import json
from datetime import datetime

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
        # Run ImageMagick to convert the TIF to a PNG format in memory
        command = [
            "C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",
            "convert",
            tif_file,
            "-quiet",
            "-background", "none",
            "-flatten",
            "-transparent", "white",
            "PNG:-"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Load the resulting PNG bytes into a Wand Image object
        img = Image(blob=result.stdout)

        # Trim whitespace from the image
        img.trim()

        return img
    except subprocess.CalledProcessError as e:
        print(f"Error processing TIF: {tif_file} - {e.stderr.decode('utf-8')}")
        return None

def create_banner(item_numbers, caption, event_code):
    """
    Creates a banner by placing flattened product images (TIF) on a background image (bg.png),
    adds a spacer and caption, and saves it to the root directory.

    Args:
        item_numbers (list): List of item numbers representing the TIF files.
        caption (str): Caption text to be added to the banner.
        event_code (str): 4-letter event code of the event for color scheme.
    """

    # Load event data from JSON file
    with open("events.json", "r") as f:
        events = json.load(f)

    if event_code not in events["events"]:
        raise ValueError(f"Invalid event code: {event_code}. Please check your events.json file.")

    caption_color = events["events"][event_code].get("spacer_color", "gray")
    spacer_color = events["events"][event_code].get("caption_color", "black")
    event_full_name = events["events"][event_code]["full_name"].lower().replace("'", "").replace(" ", "-")

    background_path = os.path.join(os.getcwd(), "bg.png")

    if not os.path.exists(background_path):
        raise FileNotFoundError("Background image 'bg.png' not found in the current directory.")

    # Open the background image as the canvas
    with Image(filename=background_path) as canvas:

        # Draw horizontal spacer above the caption (behind items)
        spacer_y = canvas.height - 100  # Position the spacer 100px above the bottom
        with Drawing() as draw:
            draw.stroke_color = Color(spacer_color)  # Spacer color from JSON
            draw.stroke_width = 8  # Thicker spacer line
            draw.line((0, spacer_y), (canvas.width, spacer_y))  # Horizontal line
            draw(canvas)

        for item_number in item_numbers:
            tif_file = os.path.join(os.environ.get("TIFF_DIRECTORY"), f"{item_number}.tif")

            if not os.path.exists(tif_file):
                print(f"Warning: TIF file for item {item_number} not found. Skipping.")
                continue

            # Flatten the TIF and load it into memory
            img = flatten_tif_to_image_in_memory(tif_file)
            if not img:
                continue

            # Resize the image to fit within 75% of the canvas height while maintaining aspect ratio
            max_height = int(canvas.height * 0.75)
            max_width = int(canvas.width * 0.9)
            img.transform(resize=f"{max_width}x{max_height}>")

            # Debug: Log resized dimensions
            print(f"Resized image dimensions: {img.width}x{img.height}")

            # Center the product image on the canvas
            x = (canvas.width - img.width) // 2
            y = (canvas.height - img.height - 70) // 2  # Adjust to slightly overlap the spacer

            # Composite the product image on top of the canvas
            canvas.composite(img, left=x, top=y)
            img.close()  # Free memory for the image

        # Add caption text centered at the bottom
        with Drawing() as draw:
            draw.font = "Arial-Bold"
            draw.font_size = 45  # Match the larger font size in the sample
            draw.fill_color = Color(caption_color)  # Caption color from JSON
            draw.text_alignment = "center"
            draw.text(canvas.width // 2, canvas.height - 40, caption)  # Position caption closer to spacer
            draw(canvas)

        # Debug: Output final canvas dimensions
        print(f"Canvas dimensions: {canvas.width}x{canvas.height}")

        # Generate output filename
        caption_hyphenated = caption.lower().replace(" ", "-")
        timestamp = datetime.now().strftime("%m%d")
        output_filename = f"4sgm-{event_full_name}-wholesale-{caption_hyphenated}-{timestamp}.webp"
        output_path = os.path.join(os.getcwd(), output_filename)

        # Save the final image as WEBP
        canvas.format = 'webp'
        canvas.save(filename=output_path)
        print(f"Banner saved to: {output_path}")  # Debug: Confirm save location

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a banner with product images.")
    parser.add_argument("item_numbers", nargs="+", help="Item numbers of the products (e.g., 123456)")
    parser.add_argument("-c", "--caption", required=True, help="Caption text for the banner")
    parser.add_argument("-e", "--event", required=False, help="4-letter event code (e.g., 'MOMD', 'VLTN')")
    args = parser.parse_args()

    create_banner(args.item_numbers, args.caption, args.event)
