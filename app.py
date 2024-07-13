import streamlit as st

clasififacion_page = st.Page("paginas/clasificacion.py", title="Clasificación", icon=":material/add_circle:")
admin_page = st.Page("paginas/admin.py", title="Admin")

pg = st.navigation([clasififacion_page, admin_page])
pg.run()





