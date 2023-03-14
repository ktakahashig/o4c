import streamlit as st
import pandas as pd
import requests
import openai
import o4c
import ast

openai.api_key  = st.secrets["OPENAI_API_KEY"]

interpretaciones_resumidas='interpretaciones_resumidas.csv'
interpretaciones = pd.read_csv(interpretaciones_resumidas)
interpretaciones['embeddings']=interpretaciones.embeddings.apply(
    lambda s: list(ast.literal_eval(s)))

st.title('ClimaCiencia')

st.header('Reporte de interpretaciones')
st.write('Ingrese abajo su consulta para buscar entre las interpretaciones disponibles en el Observatorio del Conocimiento Científico sobre Cambio Climático O4C y generar un reporte automatizado con inteligencia artificial.')

query = st.text_input("Busque en el O4C:" )
st.write('Presione Enter al finalizar y espere mientras se genera el reporte.')

if query != '':
    with st.spinner('Trabajando ...'):
        report=o4c.search_n_summarize(interpretaciones,query)
    st.success("Reporte generado con IA basado en interpretaciones más relevantes a: "+query+"\n\n")
    st.write(report)


st.caption('Autor: Ken Takahashi, \n 2023')
st.caption('Observatorio del Conocimiento Científico sobre Cambio Climático')
st.caption('Instituto Geofísico del Perú')
