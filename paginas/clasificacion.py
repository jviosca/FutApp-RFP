
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(worksheet="registro_partidos",
                ttl="10m",
                nrows=5)
                
st.title("Real Futbal Patata App")                
# show dataframe
st.dataframe(df)

