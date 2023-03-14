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

st.title('O4C')

query = st.text_input("Busque en el O4C:" ) 

with st.spinner('Pensando ...'):
   report=o4c.search_n_summarize(interpretaciones,query)

st.success("Reporte basado en interpretaciones más relevantes a: "+query+"\n\n")

st.write(report)
