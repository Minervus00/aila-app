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
