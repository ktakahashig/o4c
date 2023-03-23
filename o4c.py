def leer_interpretaciones(archivo="Interpretaciones O4C (Respuestas) - Respuestas de formulario 1.csv"):
    import pandas as pd
    import warnings
    warnings.filterwarnings("ignore")
    interpretaciones = pd.read_csv(archivo)
    interpretaciones['Marca temporal']=pd.to_datetime(interpretaciones['Marca temporal'],
                                                      format="%d/%m/%Y %H:%M:%S")
    interpretaciones['Apellidos, Nombres']=[interpretaciones['Apellidos de intérprete'][i].strip() + ", " + 
                                            interpretaciones['Nombres de intérprete'][i].strip()
                                             for i in range(len(interpretaciones))]
    interpretaciones['Apellidos, Nombres']=interpretaciones['Apellidos, Nombres'].str.title()
    interpretaciones = interpretaciones.rename(columns={interpretaciones.columns[4]: 'DOI', 
                                                        interpretaciones.columns[5]: 'Título',
                                                        interpretaciones.columns[6]: 'Resultados', 
                                                        interpretaciones.columns[7]: 'Metodología',
                                                        interpretaciones.columns[8]: 'Limitaciones', 
                                                        interpretaciones.columns[9]: 'Palabras clave',
                                                        interpretaciones.columns[12]: 'Ámbito geográfico', 
                                                        interpretaciones.columns[13]: 'Escala'})
    interpretaciones = interpretaciones.drop(interpretaciones.columns[15:22], axis=1)
    interpretaciones['Adaptación'] = interpretaciones['Adaptación'].str.replace(r'\([^)]*\)', '')
    interpretaciones['Mitigación'] = interpretaciones['Mitigación'].str.replace(r'\([^)]*\)', '')
    #
    # Limpiar la base de datos
    interpretaciones['Apellidos, Nombres'] = interpretaciones['Apellidos, Nombres'].replace(
        'Silva Vidal, Yamina','Silva Vidal, Fey Yamina')
    interpretaciones['Apellidos, Nombres'] = interpretaciones['Apellidos, Nombres'].replace(
        'Flores Rojas, José','Flores Rojas, José Luis')
    interpretaciones['Apellidos, Nombres'] = interpretaciones['Apellidos, Nombres'].replace(
        'Martínez, Alejandra G.','Martinez Grimaldo, Alejandra G.')
    interpretaciones['Apellidos, Nombres'] = interpretaciones['Apellidos, Nombres'].replace(
        'Díaz Llatas, Dianadiazll','Díaz Llatas, Diana')
    interpretaciones['Apellidos, Nombres'] = interpretaciones['Apellidos, Nombres'].replace(
        'Mosquera Váquez, Kobi Alberto','Mosquera Vásquez, Kobi Alberto')
    interpretaciones['DOI'] = interpretaciones['DOI'].str.replace('DOI: ','', regex=True)
    interpretaciones['DOI'] = interpretaciones['DOI'].str.replace('DOI','', regex=True)
    interpretaciones['DOI'] = interpretaciones['DOI'].str.replace('doi:','', regex=True)
    interpretaciones['DOI'] = interpretaciones['DOI'].str.replace('doi','', regex=True)
    interpretaciones['DOI'] = interpretaciones['DOI'].str.replace('/full','', regex=True)
    # Esto no funciona muy bien
    interpretaciones['DOI'] = interpretaciones['DOI'].apply(lambda x: "/".join(x.split('/')[-2:]).strip())
    # porque falla aquí
    interpretaciones.DOI[interpretaciones.DOI == '2515-7620/ab9003'] = '10.1088/2515-7620/ab9003'
    interpretaciones.DOI[interpretaciones.DOI == '1748-9326/ac0e65'] = '10.1088/1748-9326/ac0e65'
    interpretaciones.DOI[interpretaciones.DOI == '1748-9326/aa7541'] = '10.1088/1748-9326/aa7541'
    interpretaciones.DOI[interpretaciones.DOI == 'articles/s41467-020-18241-x'] = \
            '10.1038/s41467-020-18241-x'
    interpretaciones.DOI[interpretaciones.DOI == "Landscape and Urban Planning"] = \
            "10.1016/j.landurbplan.2016.03.021"
    interpretaciones['DOI'] = interpretaciones['DOI'].str.replace(' ','', regex=True)
    # Caso de DOI y titulo invertidos
    i =interpretaciones.DOI.str.contains('Hydro')
    doi = interpretaciones["Título"][i]
    titulo = interpretaciones["DOI"][i]
    interpretaciones["Título"][i]=titulo
    interpretaciones["DOI"][i]=doi
    #interpretes = pd.read_csv("interpretes.csv")
    #interpretaciones = interpretaciones.join(interpretes.set_index('Apellidos, Nombres'), 
    #                                         on='Apellidos, Nombres')
    return interpretaciones

# Para búsqueda semántica
def get_embed_interpretaciones(df):
    from openai.embeddings_utils import get_embedding
    df['Combinado']=df[["Título", "Resultados", "Metodología", "Limitaciones",\
                        "Palabras clave",'Adaptación', 'Mitigación', \
                        'Ámbito geográfico',  'Escala']].apply(lambda x: ' '.join(x.astype(str)), axis=1)
    df['embeddings'] = [get_embedding(x,engine="text-embedding-ada-002") for x in df.Combinado]
    df.to_csv('interpretaciones_embeddings.csv')
    return df

def semantic_search(df, query):
    from openai.embeddings_utils import get_embedding,cosine_similarity
    query_embedding = get_embedding(query, engine="text-embedding-ada-002")
    df["similarity"] = df.embeddings.apply(lambda x: cosine_similarity(x, query_embedding))
    return df

# Hacer la búsqueda semántica y obtener la similaridad coseno
def do_search(interpretaciones,query,min_similarity,max_results):
    results = semantic_search(interpretaciones, query).sort_values('similarity', ascending=False)
    results = results[results.similarity>min_similarity][:max_results]
    return results

# Hacer el reporte basado en las interpretaciones más cercanas a la consulta
def do_summary(results,query):
    import openai
    # Preparar lista de Referencias :: Resultados y conclusiones para el prompt
    dum=results[['Referencia','Resultados cortos']].drop_duplicates()
    lista_resultados = ''
    for index, row in dum.iterrows():
        lista_resultados += ' :: '.join(row.astype(str)) + '\n'    
    # Preparar lista de referencias para añadir al reporte
    dum=results[['Referencia','DOI','Apellidos, Nombres','similarity']]
    dum=dum.sort_values(by=['Referencia']).drop_duplicates()
    bibliografia = ''
    for index, row in dum.iterrows():
        bibliografia += row[0].strip()+': https://doi.org/'+row[1].strip()+ " (intérp.: " \
                     + row[2].strip()+'; sim. = '+"{:4.2f}".format(row[3]).strip()+')\n\n'   
    message_sys = """
        Eres un científico experto en el clima y estás apoyando a autoridades en el Perú para 
        elaborar los planes de gestión del cambio climático.
        """
    message_user = """
        Haz una síntesis del conocimiento científico sobre el tema "<Tema>" contenido en los 
        siguientes resultados de investigaciones científicas, los cuales son proporcionados 
        en la forma Referencia :: Resultados. Debes citar todas las referencias relevantes al tema "<Tema>".
        El texto que escribas debe tener la forma de un reporte técnico en español, agrupando los resultados 
        similares en párrafos, sobre todo los resultados de la mismas referencias, y debes hacer 
        la citación de cada una de las referencias que tenga relación con el tema "<Tema>"  en la forma "nombres (año)" o 
        "(nombres, año)". En caso de contarse con una sola referencia, hacer un breve resumen.
        No incluyas ninguna referencia que no esté indicada a continuación.
    Referencia :: Resultados
    <Referencias>
    
    Debes citar todas las referencias y el texto debe tener la forma de un reporte técnico en español, 
    agrupando los resultados similares en párrafos. Si no hay referencias relevantes al tema "<Tema>", no hagas el reporte e indica 
        "Lo sentimos. No contamos con información suficientemente relevante."
    """
    message_assist = """
    Reporte técnico sobre <Tema>:
    """
    message_user = message_user.replace("<Tema>", query)
    message_user = message_user.replace("<Referencias>", lista_resultados)
    message_assist = message_assist.replace("<Tema>", query)
    messages = [{"role": "system", "content": message_sys},{"role": "user", "content": message_user},
                {"role": "assistant", "content": message_assist}]
    # Correr el modelo y obtener el reporte
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages, max_tokens=1800, 
                                            n=1, stop=None, temperature=0.2)
    report = response['choices'][0]['message']['content'].strip()
    report = report+"\n\nReferencias:\n\n"+bibliografia
    return report

def search_n_summarize(interpretaciones,query,min_similarity = 0.77,max_results = 10):
    results = do_search(interpretaciones,query,min_similarity,max_results)
    if len(results)>0:
        report = do_summary(results,query)
    else:
        report = "Lo sentimos. No contamos con información suficientemente relevante."
    #print(report)
    return report

def slow_print_words(text, delay=0.02):
    import time
    text =text.replace('\n','_newline_ ')
    words = text.split()
    for word in words:
        word=word.replace('_newline_','\n')
        print(word, end=' ', flush=True)
        time.sleep(delay)
    print()
