# PDF Data Extraction

## About
This is a simple Python project that extracts text from PDF files using OCR.

It converts PDF pages into images, crops selected areas and extracts text from them.

## Features
- Converts PDF pages into images.
- Crops selected areas from images.
- Extracts text using OCR.
- Saves extracted data in JSON format.
- Deletes temporary files after processing.
- Maintains log files.

## Technologies Used
- Python
- OpenCV
- Tesseract OCR
- Poppler
- JSON

## Requirements
Install the required Python libraries:

```bash
pip install opencv-python pdf2image pytesseract
```

Poppler and Tesseract OCR must also be installed and configured.

## How to Run
1. Download or clone this repository.
2. Install the required libraries.
3. Configure the PDF field settings.
4. Provide the required file paths.
5. Run the Python program.

## Project Structure

```text
pdf-data-extractor/
│
├── data_extraction.py
├── pdf_fields_config.json
├── requirements.txt
```

## Output
The extracted text is returned in JSON format.

## Author
Harshi
