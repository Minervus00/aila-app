from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
from langchain_text_splitters import RecursiveCharacterTextSplitter


# read pdf file and return text
def get_pdf_text(file):
    # print(file, type(file))
    text = ""
    # Read the PDF file using PdfReader
    pages_reader = PdfReader(file)

    # Loop through each page in the PDF
    for page_num, page in enumerate(pages_reader.pages):
        page_text = page.extract_text()

        if page_text and page_text.strip():  # If the page has selectable text, add it
            text += page_text
        else:
            # If no text, assume it's a scanned page and apply OCR
            print(f"Applying OCR on page {page_num + 1}")
            # Convert the PDF page to an image (pdf2image)
            file.seek(0)  # Ensure the file pointer is at the start
            images = convert_from_bytes(file.read(), first_page=page_num+1, last_page=page_num+1)
            for image in images:
                ocr_text = pytesseract.image_to_string(image)
                text += ocr_text

    return text


# split text into chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400
    )
    chunks = splitter.split_text(text)
    return chunks  # list of strings
