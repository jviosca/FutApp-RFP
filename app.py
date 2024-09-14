import streamlit as st
import aux_functions as aux

st.session_state.temporadas,st.session_state.partidos,st.session_state.jugadores,st.session_state.mvp = aux.leer_gsheets(aux.create_gsheets_connection())

clasififacion_page = st.Page("paginas/clasificacion.py", title="Clasificación", icon=":material/add_circle:")
admin_page = st.Page("paginas/admin.py", title="Admin")

pg = st.navigation([clasififacion_page, admin_page])
pg.run()





