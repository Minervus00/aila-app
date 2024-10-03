import streamlit as st
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from utils import get_pdf_text


genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", client=genai,
                               temperature=0.3)


# split text into chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=200)
    chunks = splitter.split_text(text)
    return chunks  # list of strings


# get embeddings for each chunk
def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001")  # type: ignore
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():
    prompt_template = (
        "Always answer in the same language as the question. Answer the "
        "question with all details in the provided context. Make sure to "
        "provide all the details. if the answer is not in provided context "
        "just say, in the same language as the question, that the answer "
        "is not available in the context, don't provide the wrong answer.\n\n"
        "Context:\n {context}\n"
        "Question: \n{question}\n"
    )

    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])
    chain = create_stuff_documents_chain(llm=model, prompt=prompt)
    return chain


def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Upload some pdfs and ask me a question"}
    ]
    st.session_state.input_disabled = True


def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001")  # type: ignore

    new_db = FAISS.load_local("faiss_index", embeddings,
                              allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    # Adjust context from chat history
    docs.extend([
        Document(msg["content"]) for msg in st.session_state.messages[-3:-1]
    ])

    response = chain.invoke(
        {"context": docs, "question": user_question})

    # print(response)
    return response


def process(pdf_docs):
    if pdf_docs:
        st.session_state.input_disabled = False


st.set_page_config(
    page_title="AiLA Chat",
    page_icon="🤖"
)

# Sidebar for uploading PDF files
with st.sidebar:
    st.title("Menu:")
    pdf_docs = st.file_uploader(
        "Upload your PDF Files and Click on the Submit & Process Button",
        accept_multiple_files=True)
    if st.button("Submit & Process", on_click=process, args=(pdf_docs,)):
        with st.spinner("Processing..."):
            if pdf_docs:
                for doc in pdf_docs:
                    raw_text = get_pdf_text(doc)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                st.success("Done")
            else:
                st.warning("No Files Found.")

# Main content area for displaying chat messages
st.title("Chat with Your PDF Files 🗂️")
st.write("")
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Chat input
# Placeholder for chat messages
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Upload some PDFs and ask me a question"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.get("input_disabled") is None:
    st.session_state.input_disabled = True

if prompt := st.chat_input(disabled=st.session_state.input_disabled):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Display chat messages and bot response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = user_input(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            # placeholder.markdown(full_response)
    if response is not None:
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
