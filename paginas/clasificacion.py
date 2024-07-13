import streamlit as st
import aux_functions as aux


                
st.title("Real Futbal Patata App")          
st.header("Clasificación")          
temporadas,partidos,jugadores,mvp = aux.leer_gsheets(aux.create_gsheets_connection())
#temporada_elegida = st.selectbox("Escoge temporada",temporadas['nombre'])
clasificacion_df = aux.clasificacion(partidos,jugadores,mvp)
st.table(clasificacion_df)
