import streamlit as st
import aux_functions as aux


                
st.title("Real Futbal Patata App")          
st.header("Clasificación")          
temporadas,partidos,jugadores,mvp = aux.leer_gsheets(aux.create_gsheets_connection())
temporada_elegida_años = st.selectbox("Escoge temporada",temporadas['nombre'])
temporada_elegida_n = temporadas.loc[temporadas['nombre']==temporada_elegida_años]['numero'].values[0]
st.write(temporada_elegida_n)
st.write(type(temporada_elegida_n))
st.write(partidos.dtypes)
# filtramos la temporada
mvp['temporada_n'] = mvp['Jornada'].apply(lambda x: int(x.split('Temporada ')[1][:-1]))
mvp_temporada_elegida = mvp.loc[mvp['temporada_n']==temporada_elegida_n]
partidos_temporada_elegida = partidos.loc[partidos['temporada']==temporada_elegida_n]
#st.dataframe(partidos_temporada_elegida)
if partidos_temporada_elegida.shape[0] > 0:
    clasificacion_df = aux.clasificacion(partidos_temporada_elegida,jugadores,mvp_temporada_elegida)
    st.table(clasificacion_df)
else:
    st.write("No hay partidos en la temporada elegida")
