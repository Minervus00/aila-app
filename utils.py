from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# read pdf file and return text
def get_pdf_text(file):
    text = ""
    pages_reader = PdfReader(file)
    for page in pages_reader.pages:
        text += page.extract_text()
    return text


# split text into chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    return chunks  # list of strings
