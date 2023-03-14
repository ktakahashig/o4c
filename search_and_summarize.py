import streamlit as st
import pandas as pd
import requests
import openai
import o4c
import ast
import time
import re

openai.api_key  = st.secrets["OPENAI_API_KEY"]

interpretaciones_resumidas='interpretaciones_resumidas.csv'
interpretaciones = pd.read_csv(interpretaciones_resumidas)
interpretaciones['embeddings']=interpretaciones.embeddings.apply(
    lambda s: list(ast.literal_eval(s)))

st.title('ClimaCiencia')
st.caption('Observatorio del Conocimiento Científico sobre Cambio Climático O4C, Instituto Geofísico del Perú')
#st.caption('Instituto Geofísico del Perú')

st.header('Reporte de interpretaciones con IA')
st.write('Ingrese abajo su consulta para buscar entre las interpretaciones disponibles en el Observatorio del Conocimiento Científico sobre Cambio Climático O4C y generar un reporte automatizado con inteligencia artificial.')

query = st.text_input("Busque en el O4C (presione Enter al finalizar):" )
#st.write('Presione Enter al finalizar y espere mientras se genera el reporte.')

if query != '':
    with st.spinner('Espere mientras la IA genera el reporte ...'):
        report=o4c.search_n_summarize(interpretaciones,query)
    st.success("Reporte generado con IA basado en interpretaciones más relevantes a: "+query+"\n\n")
    p = st.empty()
    # Split the paragraph into sentences using the newline character as a delimiter
    sentences = report.split("\n")
    # Split each sentence into words using regular expressions
    words = [re.findall(r'\w+|[^\w\s]', sentence) for sentence in sentences]
    text = ""
    for sentence in words:
        for word in sentence:
            text= text + word + " "
            p.write(text)
            time.sleep(0.02)
        text = text + "\n"



paragraphs = report.split("\n\n")  # Split text into paragraphs
text = ""
for paragraph in paragraphs:
    words = []
    current_word = ""
    for character in paragraph:
        if character.isalnum() or character == "'":  # Preserve alphanumeric characters and apostrophes
            current_word += character
        else:
            if current_word:
                words.append(current_word)
                current_word = ""
            words.append(character)
    if current_word:
        words.append(current_word)
    for word in words:
        text= text + word
        p.write(text)
        time.sleep(0.02)

st.caption('Autor: Ken Takahashi, \n 2023')

