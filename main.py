import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

_, col1, _ = st.columns([1, 3, 1])

st.sidebar.success("Select an app above.")

with col1:
    st.image("aila-rmbg.png", "AiLA - AI to Learn Actively",
             use_column_width="auto")

    st.html("""<h1 style='font-weight:bold; text-align:center;
            font-family:rockwell; margin-left: 2vw'>
            Hi, I'm AiLA !
            </h1>""")
st.write("")
st.write("")

st.markdown(
    """
    ### I'm here to help you have a better understanding of your documents, lectures or articles.
    ### By Uploading your files here, you can:
    - Chat with me about your uploaded documents
    - Generate a Multiple Choices Quizz
    - Generate a True-False Quizz

    #### 👈 Select an app from the sidebar
    """
)
