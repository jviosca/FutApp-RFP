import streamlit as st

st.write("Hello world")
st.write("Pronto aquí estará la clasificación de Real Futbal Patata")

from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read()

# Print results.
for row in df.itertuples():
    st.write(row)
