def my_app():
    import streamlit as st
    import pinecone
    import pandas as pd
    import requests
    import openai
    import o4c
    import ast
    import time
    import re

    openai.api_key  = st.secrets["OPENAI_API_KEY"]
    pinecone.init(api_key=st.secrets["PINECONE_API_KEY"],environment='us-central1-gcp')
    index_name = "o4c"
    index = pinecone.Index(index_name=index_name)

    st.title('CienciaClimática')
    st.caption('Observatorio del Conocimiento Científico sobre Cambio Climático, Instituto Geofísico del Perú')

    st.header('Reporte de interpretaciones con IA (demo)')
    st.write('Ingrese abajo su consulta para buscar entre las interpretaciones disponibles en el Observatorio del Conocimiento Científico sobre Cambio Climático O4C y generar un reporte automatizado con inteligencia artificial.')

    opciones=['Resultados y Conclusiones','Limitaciones de los estudios','Plan de investigación']
    opcion=st.radio("Elija sobre qué desea reportar:", options=opciones)

    query = st.text_input("Busque en el Observatorio:" )

    st.caption('Presione Enter (o a la derecha de la barra en dispositivos móviles) al finalizar y espere')



    if query != '':
        if opcion == opciones[0]:
            with st.spinner('Espere mientras la IA genera el reporte ...'):
               report=o4c.search_n_summarize(index,query,modo=0)
            st.success("Reporte generado con IA basado en interpretaciones de los resultados más relevantes a: "+query+"\n\nIMPORTANTE: El usuario es responsable de verificar que este reporte refleje fielmente el contenido de las interpretaciones.\n\n")
        elif opcion == opciones[1]:
            with st.spinner('Espere mientras la IA genera el reporte ...'):
               report=o4c.search_n_summarize(index,query,modo=1)
            st.success("Reporte generado con IA basado en interpretaciones de las limitaciones de los estudios más relevantes a: "+query+"\n\nIMPORTANTE: El usuario es responsable de verificar que este reporte refleje fielmente el contenido de las interpretaciones.\n\n")
        else: 
            with st.spinner('Espere mientras la IA genera el reporte ...'):
               report=o4c.search_n_summarize(index,query,modo=2)
            st.success("Propuesta de plan de investigación generado con IA basado en interpretaciones de las limitaciones de los estudios más relevantes a: "+query+"\n\nIMPORTANTE: El usuario es responsable de verificar que este plan cita adecuadamente las investigaciones, considerando que la IA puede dar aportes propios sin mayor sustento.\n\n")

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
