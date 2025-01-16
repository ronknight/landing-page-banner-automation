from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import os
import argparse
import json
import datetime
import math

def create_banner(item_numbers, background_path, output_dir, caption, event_code, preferred_cols=None):
    """
    Creates a banner by arranging product images (TIF) on a background (PNG) 
    in a grid layout.

    Args:
        item_numbers (list): List of item numbers representing the TIF files.
        background_path (str): Path to the background PNG image.
        output_dir (str): Path to the directory to save the WEBP banner.
        caption (str): Caption text to be added to the banner.
        event_code (str): 4-letter code of the event for color scheme.
        preferred_cols (int, optional): Preferred number of columns. 
                                        If None, it's calculated automatically.
    """

    # Load events from JSON file
    with open('events.json', 'r') as f:
        events_data = json.load(f)
    events = events_data["events"]

    # If invalid event code, show options and exit
    if event_code not in events:
        print("Invalid event code. Available options:")
        for code, data in events.items():
            print(f"{code}: {data['full_name']}")
        exit(1)

    # Get color scheme from events dictionary
    spacer_color = Color(events[event_code]["spacer_color"])
    caption_color = Color(events[event_code]["caption_color"])

    with Image(filename=background_path) as bg_img:
        bg_width = bg_img.width
        bg_height = bg_img.height

        # Analyze example image for spacing (replace with actual values)
        horizontal_spacing = 50  # Example value, get from the image
        vertical_spacing = 30    # Example value, get from the image

        tif_count = len(item_numbers)

        # Calculate optimal grid dimensions
        if preferred_cols:
            cols = preferred_cols
            rows = math.ceil(tif_count / cols)
        else:
            # Estimate the number of columns based on aspect ratio and spacing
            estimated_cols = int(math.sqrt(tif_count * bg_width / bg_height))
            best_area = float('inf')
            for cols in range(max(1, estimated_cols - 2), estimated_cols + 3):  # Check around the estimate
                rows = math.ceil(tif_count / cols)
                cell_width = (bg_width - (cols - 1) * horizontal_spacing) // cols
                total_area = rows * cols * cell_width * 462  # Approximate area
                if total_area < best_area:
                    best_area = total_area
                    best_cols = cols
                    best_rows = rows
            cols = best_cols
            rows = best_rows

        with Drawing() as draw:
            for i, item_number in enumerate(item_numbers):
                # Construct image path from environment variable
                tif_file = os.path.join(os.environ.get("TIF_PATH"), f"{item_number}.tif")  
                
                with Image(filename=tif_file) as tif_img:
                    # Resize while maintaining aspect ratio
                    tif_img.transform(resize=f'{cell_width}x{cell_height}>')

                    # Calculate position for the current cell
                    row = i // cols
                    col = i % cols
                    x = col * (cell_width + horizontal_spacing)
                    y = row * (cell_height + vertical_spacing)

                    # Center the image horizontally within the cell
                    x += (cell_width - tif_img.width) // 2

                    # Composite the TIF image onto the background
                    draw.composite(operator='over', left=x, top=y, 
                                   width=tif_img.width, height=tif_img.height, image=tif_img)

            # Add caption text centered at the bottom
            draw.font = 'Arial'  # Choose your desired font
            draw.font_size = 30   # Adjust font size as needed
            draw.fill_color = caption_color
            draw.text_alignment = 'center'  # Center the caption
            caption_metrics = draw.get_font_metrics(bg_img, caption)
            caption_x = bg_width // 2
            caption_y = bg_height - caption_metrics.text_height - 20  # Adjust spacing from bottom as needed
            draw.text(caption_x, caption_y, caption)

            # Apply the composite drawings to the background image
            draw(bg_img)

    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%m%d")

    # Create output filename with timestamp and event code
    output_filename = f"4sgm-{event_code}-wholesale-perfume-{timestamp}.webp"
    output_path = os.path.join(output_dir, output_filename)

    # Save the final image as WEBP
    bg_img.format = 'webp'
    bg_img.save(filename=output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a banner with product images.")
    parser.add_argument("item_numbers", nargs="+", help="Item numbers of the products (e.g., 123456)")
    parser.add_argument("-b", "--background", required=True, help="Path to the background PNG image")
    parser.add_argument("-c", "--caption", required=True, help="Caption text for the banner")
    parser.add_argument("-e", "--event", required=True, help="4-letter event code (e.g., 'MOMD', 'VLTN')")
    parser.add_argument("-o", "--output", default="", help="Output directory (default: current directory)")
    parser.add_argument("-cols", "--columns", type=int, help="Preferred number of columns (optional)")
    args = parser.parse_args()

    create_banner(args.item_numbers, args.background, args.output, args.caption, args.event, args.columns)