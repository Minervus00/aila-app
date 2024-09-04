from langchain_community.document_loaders import PyPDFLoader  # TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# read pdf file and return text
def get_pdf_text(file):
    text = ""
    pages = PyPDFLoader(file).load()
    for page in pages:
        text += page.page_content
    return text


# split text into chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    return chunks  # list of strings
