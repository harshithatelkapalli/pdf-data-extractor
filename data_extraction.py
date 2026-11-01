"""
PDF data extraction utility.

Converts PDF pages to images, crops configured areas, reads text with OCR,
and saves the results as JSON.
"""

import json
import shutil
from pathlib import Path

import cv2
from pdf2image import convert_from_path
from pace_data_extractor_utility import TextExtractor


def convert_pdf_to_images(pdf_file, poppler_path, temp_folder):
    """Convert every page in a PDF into a PNG image."""
    print("Converting PDF to images...")

    temp_folder = Path(temp_folder)
    temp_folder.mkdir(parents=True, exist_ok=True)

    pages = convert_from_path(
        str(pdf_file),
        poppler_path=str(poppler_path)
    )

    for page_number, page in enumerate(pages, start=1):
        image_file = temp_folder / f"page{page_number}.png"
        page.save(image_file, "PNG")
        print(f"Saved {image_file.name}")

    return len(pages)


def crop_image(start_x, start_y, end_x, end_y, image_file, output_file):
    """Crop one area from an image and save it."""
    image = cv2.imread(str(image_file))

    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_file}")

    height, width = image.shape[:2]

    # Check that the crop coordinates are inside the image.
    if not (
        0 <= start_x < end_x <= width
        and 0 <= start_y < end_y <= height
    ):
        raise ValueError(
            f"Crop coordinates are outside the image: {image_file}"
        )

    cropped_image = image[start_y:end_y, start_x:end_x]

    saved = cv2.imwrite(str(output_file), cropped_image)
    if not saved:
        raise OSError(f"Could not save cropped image: {output_file}")

    return output_file


def read_config(config_file):
    """Read the field names and crop coordinates from a JSON file."""
    with open(config_file, "r", encoding="utf-8") as file:
        config = json.load(file)

    if "fields" not in config:
        raise ValueError("The config file must contain a 'fields' section.")

    return config


def extract_text(image_file, tesseract_config):
    """Read text from an image using the project's TextExtractor."""
    extractor = TextExtractor(str(tesseract_config))
    text = extractor.extract_text_from_file(
        str(image_file),
        method="image"
    )

    return text or ""


def clean_folder(folder):
    """Delete files and subfolders inside the temporary folder."""
    folder = Path(folder)

    if not folder.exists():
        return

    for item in folder.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print("Temporary folder cleaned.")


def save_result(result, output_file):
    """Save the extracted fields as a JSON file."""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"Results saved to {output_file}")


def extract_data(
    pdf_file,
    config_file,
    temp_folder,
    poppler_path,
    tesseract_config,
    output_file=None
):
    """
    Run the complete PDF extraction process.

    The JSON config decides which page and image coordinates to read.
    """
    temp_folder = Path(temp_folder)
    result = {}

    try:
        # Start with an empty temporary folder.
        temp_folder.mkdir(parents=True, exist_ok=True)
        clean_folder(temp_folder)

        # Load the field settings and convert the PDF.
        config = read_config(config_file)
        page_count = convert_pdf_to_images(
            pdf_file, poppler_path, temp_folder
        )

        # Read each field listed in the config file.
        for field_name, details in config["fields"].items():
            print(f"Reading field: {field_name}")

            page_number = int(details["page"])
            if page_number < 1 or page_number > page_count:
                raise ValueError(
                    f"Page {page_number} for '{field_name}' "
                    f"is not in this PDF."
                )

            page_image = temp_folder / f"page{page_number}.png"
            cropped_image = temp_folder / f"{field_name}.png"

            crop_image(
                int(details["start_x"]),
                int(details["start_y"]),
                int(details["end_x"]),
                int(details["end_y"]),
                page_image,
                cropped_image
            )

            text = extract_text(cropped_image, tesseract_config)

            # Remove the page marker used by the OCR utility, if present.
            text = text.replace("--- Page 1 ---", "")
            result[field_name] = text.strip()

        if output_file:
            save_result(result, output_file)

        print("PDF extraction completed.")
        return json.dumps(result, indent=4, ensure_ascii=False)

    except Exception as error:
        print(f"PDF extraction failed: {error}")
        raise

    finally:
        # Remove temporary page images and cropped images.
        clean_folder(temp_folder)


if __name__ == "__main__":
    # Change these paths to match your computer before running.
    pdf_path = "sample.pdf"
    config_path = "pdf_fields_config.json"
    temp_path = "temp"
    poppler_path = r"C:\poppler\Library\bin"
    tesseract_config_path = "config.ini"
    output_path = "output/extracted_data.json"

    extracted_json = extract_data(
        pdf_path,
        config_path,
        temp_path,
        poppler_path,
        tesseract_config_path,
        output_path
    )

    print(extracted_json)
