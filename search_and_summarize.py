"""
#### For azure
import streamlit as st
from gunicorn.app.base import BaseApplication

class StreamlitApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def app(environ, start_response):
    if environ.get('PATH_INFO', '').startswith('/'):
        st_app = my_app
    else:
        st_app = my_app
    return st_app(environ, start_response)

def run_streamlit_app(app, port=5000):
    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': 1,
    }
    StreamlitApp(app, options).run()

if __name__ == '__main__':
    run_streamlit_app(app)
####
"""

def my_app():
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

    st.title('CienciaClimática')
    st.caption('Observatorio del Conocimiento Científico sobre Cambio Climático, Instituto Geofísico del Perú')

    st.header('Reporte de interpretaciones con IA (demo)')
    st.write('Ingrese abajo su consulta para buscar entre las interpretaciones disponibles en el Observatorio del Conocimiento Científico sobre Cambio Climático O4C y generar un reporte automatizado con inteligencia artificial.')

    query = st.text_input("Busque en el Observatorio:" )
    st.caption('Presione Enter (o a la derecha de la barra en dispositivos móviles) al finalizar y espere')

    if query != '':
        with st.spinner('Espere mientras la IA genera el reporte ...'):
            report=o4c.search_n_summarize(interpretaciones,query)
        st.success("Reporte generado con IA basado en interpretaciones más relevantes a: "+query+"\n\n")
        p = st.empty()
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
            text = text + "\n\n"

    st.caption('© Ken Takahashi Guevara, 2023')
my_app()
