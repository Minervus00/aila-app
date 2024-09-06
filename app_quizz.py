import streamlit as st
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from utils import get_pdf_text, get_text_chunks
import random


def initialize_state():
    st.session_state.count = 0
    st.session_state.correct = 0
    if 'quizz_data' in st.session_state:
        del st.session_state['quizz_data']


def next_question():
    ss = st.session_state
    ss.count += 1
    # print(f"Moving to next question. New count: {ss.count}")
    # st.experimental_rerun()


def load_data(chunks: list, n: int, lang="français"):
    context = "\n\n".join(random.sample(chunks, n))
    prompt = f"""
{context}
-----------------
Proposes moi un quizz de {n} questions sur le contenu proposé plus haut.
Pour chaque question donnes les propositions et la bonne réponse en {lang}.
Donnes moi juste le quizz dans ta réponse et le tout sous format JSON, pas
dans un bloc, juste comme suit:
[
    {{
        "question": "...",
        "options": ["...", "...", "..."],
        "answer": 0
    }},
    {{
        "question": "...",
        "options": ["...", "...", "..."],
        "answer": 0
    }}
]
    """
    response = model.generate_content(prompt)
    # print(response.text)
    if "json" in response.text[:10]:
        quizz_data = json.loads(response.text[7:-3])
    else:
        quizz_data = json.loads(response.text)
    # print(quizz_data[0]['question'])
    return quizz_data


def launch_quizz():
    # print("\nquizz launched")
    ss = st.session_state
    if ss.count < len(ss.quizz_data):
        question = ss.quizz_data[ss.count]

        st.markdown(f"## Question {ss.count + 1}\n### {question['question']}")

        form = st.form(key=f"quiz_form_{ss.count}")
        user_choice = form.radio("Choose an answer:",
                                 question['options'], index=None)
        submitted = form.form_submit_button("Submit your answer")

        if submitted and user_choice:
            # print(f"User choice: {user_choice}")
            # print(f"Correct answer: {question['options'][question['answer']]}")
            if question['options'].index(user_choice) == question['answer']:
                st.success("Correct")
                ss.correct += 1
            else:
                st.error("Incorrect")

            txt = "Next Question" if ss.count != len(ss.quizz_data) - 1 else "Finish"
            st.button(txt, on_click=next_question)

    else:
        st.markdown("## Quiz Completed!")
        st.markdown(f"### You answered correctly {ss.correct} out of {len(ss.quizz_data)} questions.")

    # print("---------------------------")


def main():
    # Sidebar for uploading PDF files
    with st.sidebar:
        st.header("Settings")

        files = st.file_uploader(
            "Upload your PDF Files and Click on the Process Button",
            accept_multiple_files=True)

        number = st.number_input("Questions",
                                 min_value=5, max_value=20, step=5)
        st.write("Quizz questions", number)

        lang = st.selectbox("Quizz Langage",
                            ["Français", "English"])

        if st.button("✅Process"):
            initialize_state()
            if files:
                with st.spinner("Processing..."):
                    # Process pdf_docs
                    chunks = []
                    for fileDoc in files:
                        if fileDoc.name.endswith('.pdf'):
                            text = get_pdf_text(fileDoc)
                            file_chunks = get_text_chunks(text)
                            chunks.extend(file_chunks)
                    # load_data(chunks, number)
                    quizz = load_data(chunks, number, lang)
                    st.success("Done")
                st.session_state.quizz_data = quizz
                # launch_quizz()
            else:
                st.error("No document found")

    st.html('<h1 style="text-align: center; color: #6ca395;">PDF Quizz</h1>')

    if 'quizz_data' in st.session_state:
        launch_quizz()


if __name__ == '__main__':
    load_dotenv()
    os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gen_config = {
        "temperature": 0.5,
        # "top_p": 0.8,
        # "top_k": 64,
        # "max_output_tokens": 8192
    }

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config=gen_config)

    main()
