import streamlit as st
import json
import google.generativeai as genai
from utils import get_pdf_text, get_text_chunks
import random
from fpdf import FPDF


def create_quiz_pdf(quiz_data):
    """Create a PDF file from quiz data"""
    pdf = FPDF()
    pdf.add_page()

    # Add title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Quiz Questions", ln=True, align="C")
    pdf.ln(10)

    # Add questions
    pdf.set_font("Arial", "B", 12)
    for i, item in enumerate(quiz_data):
        # Question
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"Question {i+1}: {item['question']}")

        # Options
        pdf.set_font("Arial", "", 12)
        for j, option in enumerate(item["options"]):
            if item["answer"] and option[0] != "F" or \
              not item["answer"] and option[0] == "F":
                correct = "[x] "
            else:
                correct = "     "
            # correct = "✓ " if j == item["answer"] else "  "
            pdf.multi_cell(0, 10, f"{correct}Option {j+1}: {option}")

        # Explanation
        pdf.set_font("Arial", "I", 12)
        pdf.multi_cell(0, 10, f"Explanation: {item['explanation']}")
        pdf.ln(5)

    return pdf.output(dest="S").encode("latin1")


def initialize_state():
    st.session_state.tf_state = {}
    st.session_state.tf_state['response_error'] = False
    st.session_state.tf_state['count'] = 0
    st.session_state.tf_state['correct'] = 0
    st.session_state.tf_state['disable_submit'] = False


def next_question():
    ss = st.session_state.tf_state
    ss['count'] += 1
    ss['disable_submit'] = False
    # print(f"Moving to next question. New count: {ss.count}")
    # st.experimental_rerun()


def btn_disabled():
    ss = st.session_state.tf_state
    ss['disable_submit'] = True


def load_data(chunks: list, n: int, lang="français"):
    context = "\n\n".join(random.sample(chunks, min(n, len(chunks))))
    prompt = f"""
{context}
-----------------
Tu es un enseignant et tu crées un questionnaire vrai/faux de {n} questions
sur le contenu proposé plus haut, en {lang}. Donnes les réponses avec 0
pour faux et 1 pour vrai, et une explication de la bonne réponse. Donnes
moi juste le quizz dans ta réponse et le tout sous format JSON, sans encadrer
le tout avec les triples quotes juste comme suit:
[
    {{
        "question": "...",
        "options": ["Vrai", "Faux"],
        "explanation": "...",
        "answer": 0
    }},
    {{
        "question": "...",
        "options": ["Faux", "Vrai"],
        "explanation": "...",
        "answer": 1
    }}
]
    """
    try:
        response = model.generate_content(prompt)
        if "json" in response.text[:10]:
            quizz_data = json.loads(response.text[7:-3])
        else:
            quizz_data = json.loads(response.text)
        # print(quizz_data[0]['question'])
        return quizz_data
    except Exception:
        st.session_state.tf_state['response_error'] = True
        return []


def launch_quizz():
    # print("\nquizz launched")
    ss = st.session_state.tf_state
    if ss['count'] < len(ss['quizz_data']):
        question = ss['quizz_data'][ss['count']]

        st.markdown(f"## Question {ss['count'] + 1}\n### {question['question']}")

        form = st.form(key=f"quiz_form_{ss['count']}")
        user_choice = form.radio("Choose an answer:",
                                 question['options'], index=None)
        submitted = form.form_submit_button("Submit your answer",
                                            disabled=ss['disable_submit'],
                                            on_click=btn_disabled
                                            )

        if submitted and user_choice:
            # print(f"User choice: {user_choice}")
            # print(f"Corr answer: {question['options'][question['answer']]}")
            if (question['answer'] and user_choice[0] != "F") or \
               (not question['answer'] and user_choice[0] == "F"):
                st.success("Correct")
                ss['correct'] += 1
            else:
                st.error("Incorrect")

            # st.markdown("## :bulb:\n\n##### " + question["explanation"])
            st.markdown("## :bulb:")
            st.html(f"<h4 style='font-weight: normal;'>{question['explanation']}</h4>")
            st.write("")

            txt = "Next Question →" if ss['count'] != len(ss['quizz_data']) - 1 else "Finish"
            st.button(txt, on_click=next_question)

    else:
        st.markdown("## Quiz Completed!")
        st.markdown(f"### You answered correctly {ss['correct']} out of {len(ss['quizz_data'])} questions.")
        # if ss.correct/len(ss.quizz_data) > 0.7:
        # st.balloons()

    # print("---------------------------")


def main():
    # Sidebar for uploading PDF files
    with st.sidebar:
        st.header("Settings")

        files = st.file_uploader(
            "Upload your PDF Files and Click on the Process Button",
            accept_multiple_files=True)

        nb_question = st.number_input("Questions", min_value=5,
                                      max_value=20, step=5)
        st.write("")

        lang = st.selectbox("Quizz Language",
                            ["Français", "English"])

        st.write("")

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
                    quizz = load_data(chunks, nb_question, lang)
                if quizz:
                    st.success("Done", icon="✅")
                    st.session_state.tf_state['quizz_data'] = quizz
                    pdf_bytes = create_quiz_pdf(quizz)
                    st.session_state.qz_state['pdf_bytes'] = pdf_bytes
                else:
                    st.error("Error", icon="🚨")
            else:
                st.error("No document found", icon="🚨")

    st.html('<h1 style="text-align: center">AiLA <span style="color: #309078;">True-False</span>✅</h1>')

    if 'tf_state' in st.session_state:
        if 'quizz_data' in st.session_state.tf_state:
            launch_quizz()
            with st.sidebar:
                st.download_button(
                    label="⬇️Download Quiz",
                    data=st.session_state.qz_state['pdf_bytes'],
                    file_name="quiz.pdf",
                    mime="application/pdf",
                    help="Download the quiz as a PDF file",
                )

        if st.session_state.tf_state.get('response_error'):
            st.toast("An error occured, please retry !", icon="🚨")


genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
gen_config = {
    "temperature": 0.5,
    # "top_p": 0.8,
    # "top_k": 64,
    # "max_output_tokens": 8192
}

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    generation_config=gen_config)

st.set_page_config(
    page_title="AiLA True-False",
    page_icon="✅",
)

main()
