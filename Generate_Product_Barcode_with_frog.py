import barcode
import argparse
from barcode.writer import ImageWriter

from PIL import Image


def generate_barcode(data, length_mm):
    barcode_type = barcode.get_barcode_class('code128')  # Using Code 39 format
    bc = barcode_type(data, writer=ImageWriter())
    options = {"module_height": 10, "font_size": 10, "text_distance": 4, "quiet_zone": 0.9, "module_width": 0.2}

    label = bc.render(options)


    width, height = label.size

    left, top, right, bottom = 0, 10, width, height - 29
    label = label.crop((left, top, right, bottom))




    # Convert mm to pixels
    dpi = 360
    width_px = int((33 / 25.4) * dpi)
    height_px = int((12 / 25.4) * dpi)

    # Create blank image
    barcode_raw = Image.new("RGB", (width_px, height_px), "white")
    # Assuming cropped_img is already defined and has size
    label_width, label_height = label.size

    # Calculate position to center
    x_offset = (width_px - label_width) // 2
    y_offset = (height_px - label_height) // 2

    # Paste cropped_img centered in img
    barcode_raw.paste(label, (x_offset, y_offset))
    # barcode_raw.save("barcode_raw.png")

    # Convert mm to pixels
    dpi = 360
    width_px = int((41 / 25.4) * dpi)
    height_px = int((12 / 25.4) * dpi)

    # Create blank image
    img = Image.new("RGB", (width_px, height_px), "white")

    # Paste cropped_img centered in img
    img.paste(barcode_raw, (0, 0))


    # Load the image you want to add
    image_to_add = Image.open('frog.png')
    position = (width_px-120, 25)
    img.paste(image_to_add, position)



    img.save("barcode.png")


def main():

    parser = argparse.ArgumentParser(description='Generate a barcode.')
    parser.add_argument('data', type=str, help='Data to encode in the barcode')

    args = parser.parse_args()
    data = args.data

    generate_barcode(data, 33)


if __name__ == '__main__':
    main()

#  lpr -P PT-P900W -o PageSize=Custom.12x41mm -o Resolution=360dpi -o CutLabel=0 -o ExtraMargin=0mm -o number-up=1 -o orientation-requested=4 barcode.png

