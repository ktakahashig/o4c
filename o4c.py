
def semantic_search(index, query,top_k=10):
    import pandas as pd
    from openai.embeddings_utils import get_embedding
    query_embedding = get_embedding(query, engine="text-embedding-ada-002")
    query_result = index.query(query_embedding, namespace='combined',top_k=top_k)
    matches=query_result.matches
    ids = [res.id for res in matches]
    scores = [res.score for res in matches]
    results=index.fetch(ids,namespace='combined')

    columns=['Id','DOI','Referencia','Año','Título','Resultados','Resultados cortos','Metodología',
             'Limitaciones','Palabras clave','Adaptación','Mitigación','Ámbito geográfico','Escala',
             'Intérprete','Revisor']
    df = pd.DataFrame(columns=columns)

    for id in ids:
        row=[id]
        for col in columns[1:]:
            row.append(results.vectors[id].metadata[col])
        df.loc[len(df)] = row
    df['Similaridad']=scores
    df['Similaridad']=df['Similaridad'].astype(float)
    df['Año'] = df['Año'].astype(int)

    return df

# Hacer la búsqueda semántica y obtener la similaridad coseno
def do_search(index,query,min_similarity,max_results=10):
    results = semantic_search(index, query,max_results).sort_values('Similaridad', ascending=False)
    results = results[results.Similaridad>min_similarity][:max_results]
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
    dum=results[['Referencia','DOI','Intérprete','Similaridad']]
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
    agrupando los resultados similares en párrafos. 
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
                                            n=1, stop=None, temperature=0.1,top_p=0.3)
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

