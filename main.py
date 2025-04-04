import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

_, col1, _ = st.columns([1, 3, 1])

st.sidebar.success("Select an app above.")

with col1:
    st.image("images/citadel_logo.png")
    st.write("")
    st.image("images/aila-rmbg.png", "AiLA - AI to Learn Actively")

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Rockwell&display=swap');

        .rockwell-text {
            font-family: 'Rockwell', serif;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin-left: 2vw;
            padding-top: 0px;
            margin-top: 0px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<h1 class="rockwell-text">Hi, I\'m AiLA!</h1>', unsafe_allow_html=True)

    # st.html("""<h1 style='font-weight:bold; text-align:center;
    #         font-family: Rockwell; margin-left: 2vw'>
    #         Hi, I'm AiLA !
    #         </h1>""")

st.write("")
st.write("")
st.write("")
# st.write("")

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
