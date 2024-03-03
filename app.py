import PyPDF2
import openai
import streamlit as st
import re
from collections import Counter

openai.api_key = 'OPENAI-API-KEY'

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text() + "\n\n"
    return text

def get_paragraphs(text):
    return [para for para in text.split('\n\n') if para.strip() != '']

def get_keywords(text):
    return set(re.findall(r'\w+', text.lower()))

def is_question_relevant(question, paragraphs, threshold=0.3):
    question_keywords = get_keywords(question)
    for paragraph in paragraphs:
        paragraph_keywords = get_keywords(paragraph)
        common_keywords = question_keywords.intersection(paragraph_keywords)
        if common_keywords and len(common_keywords) / len(question_keywords) >= threshold:
            return True
    return False

def ask_question_to_gpt4(question, pdf_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106", 
        messages=[
            {"role": "system", "content": "Bu bir sohbet oturumudur."},
            {"role": "user", "content": pdf_text},
            {"role": "user", "content": f"Soru: {question}"}
        ],
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].message['content'].strip()

# Streamlit uygulaması
st.title("ChatPDF")

uploaded_file = st.file_uploader("PDF dosyası yükle", type="pdf")
question = st.text_input("Sorunuzu buraya yazın")

if uploaded_file is not None and question:
    pdf_text = extract_text_from_pdf(uploaded_file)
    paragraphs = get_paragraphs(pdf_text)

    if is_question_relevant(question, paragraphs):
        answer = ask_question_to_gpt4(question, pdf_text)
        st.write("Cevap:", answer)
    else:
        st.write("Sorduğunuz sorunun cevabı bu belgede bulunmamaktadır.")
