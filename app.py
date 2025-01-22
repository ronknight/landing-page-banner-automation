import os
import argparse
import subprocess
from io import BytesIO
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from dotenv import load_dotenv

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
            "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe",
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
        return Image(blob=result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error processing TIF: {tif_file} - {e.stderr.decode('utf-8')}")
        return None

def create_banner(item_numbers, caption, event_code):
    """
    Creates a banner by placing flattened product images (TIF) on a transparent canvas
    and saves it to the root directory.

    Args:
        item_numbers (list): List of item numbers representing the TIF files.
        caption (str): Caption text to be added to the banner.
        event_code (str): 4-letter code of the event for color scheme.
    """

    canvas_width = 500  # Example width for the transparent canvas
    canvas_height = 500  # Example height for the transparent canvas

    with Image(width=canvas_width, height=canvas_height, background=Color("transparent")) as canvas:
        canvas.alpha_channel = 'activate'  # Ensure the canvas has a transparent background

        for item_number in item_numbers:
            tif_file = os.path.join(os.environ.get("TIFF_DIRECTORY"), f"{item_number}.tif")

            if not os.path.exists(tif_file):
                print(f"Warning: TIF file for item {item_number} not found. Skipping.")
                continue

            # Flatten the TIF and load it into memory
            img = flatten_tif_to_image_in_memory(tif_file)
            if not img:
                continue

            # Resize the image to 70% of the canvas size while maintaining aspect ratio
            scale_factor = 0.7
            max_width = int(canvas_width * scale_factor)
            max_height = int(canvas_height * scale_factor)
            img.resize(min(img.width, max_width), min(img.height, max_height))

            # Debug: Log resized dimensions
            print(f"Resized image dimensions: {img.width}x{img.height}")

            # Center the product image on the canvas
            x = (canvas_width - img.width) // 2
            y = (canvas_height - img.height - 100) // 2
            print(f"Positioning image at: ({x}, {y})")  # Debug: Log position

            # Composite the image onto the canvas
            canvas.composite(img, left=x, top=y)
            img.close()  # Free memory for the image

        # Draw horizontal spacer above the caption
        spacer_y = canvas_height - 100  # Position the spacer 100px above the bottom
        with Drawing() as draw:
            draw.stroke_color = Color("gray")  # Spacer color
            draw.stroke_width = 2
            draw.line((0, spacer_y), (canvas_width, spacer_y))  # Horizontal line
            draw(canvas)

        # Add caption text centered at the bottom
        with Drawing() as draw:
            draw.font = "Arial"
            draw.font_size = 20
            draw.fill_color = Color("black")
            draw.text_alignment = "center"
            draw.text(canvas_width // 2, canvas_height - 50, caption)  # Position caption
            draw(canvas)

        # Debug: Output final canvas dimensions
        print(f"Canvas dimensions: {canvas_width}x{canvas_height}")

        # Generate output filename
        output_filename = f"banner-{event_code}.webp"
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
