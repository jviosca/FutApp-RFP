import hmac
import streamlit as st
import sys


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets.authentication["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Main Streamlit app starts here
st.title("Real Futbal Patata App")

tab1,tab2 = st.tabs(["Partidos", "Configuración"])
with tab1:
    st.header("Registro de goles en los partidos")
    st.write("En esta pestaña elige los jugadores de cada partido y anota los goles que ha metido cada uno.")
    st.write("Para añadir jornadas, temporadas y jugadores, utiliza la pestaña 'Configuración'.")
    st.write("Hasta que no apretes el botón 'Guardar' abajo del todo, no se guardarán los cambios.")
    col1a,col1b = st.columns(2)
    with col1a:
        temporada_elegida_años = st.selectbox("Escoge temporada",st.session_state.temporadas['nombre'], index=len(st.session_state.temporadas['nombre'])-1)
        temporada_elegida_n = st.session_state.temporadas.loc[st.session_state.temporadas['nombre']==temporada_elegida_años]['numero'].values[0]
    with col1b:
        partidos_temporada_elegida = st.session_state.partidos.loc[st.session_state.partidos['temporada']==temporada_elegida_n]
        jornadas_n = partidos_temporada_elegida['jornada'].unique()
        jornadas_con_fechas = ["Jornada " + str(int(item)) + " (" + partidos_temporada_elegida.loc[partidos_temporada_elegida['jornada']==item]['fecha'].unique()[0] + ")" for item in jornadas_n] 
        jornada_elegida = st.selectbox("Escoge jornada", jornadas_con_fechas, index = len(partidos_temporada_elegida['jornada'].unique())-1)
        jornada_elegida_n = int(jornada_elegida[8:].split('(',1)[0].strip())
    # recuperamos datos guardados de la jornada
    datos_jornada_elegida = partidos_temporada_elegida.loc[partidos_temporada_elegida['jornada']==jornada_elegida_n]
    # separamos datos en los 2 equipos. En temporada 1 no hay columna equipo, 
    # pero en temporada 2 la añadimos para poder separar los datos. Posibles 
    # valores son A o B
    equipo_A = datos_jornada_elegida.loc[datos_jornada_elegida['equipo']=='A'].sort_values(by="jugador", key=lambda col: col.str.lower())
    equipo_B = datos_jornada_elegida.loc[datos_jornada_elegida['equipo']=='B'].sort_values(by="jugador", key=lambda col: col.str.lower())
    equipo_A_goles_metidos = equipo_B['goles_recibidos'].unique()[0]
    equipo_A_goles_recibidos = equipo_A['goles_recibidos'].unique()[0]
    equipo_B_goles_metidos = equipo_A['goles_recibidos'].unique()[0]
    equipo_B_goles_recibidos = equipo_B['goles_recibidos'].unique()[0]

    with st.form("Registro de goles y jugadores"):
        col2a,col2b = st.columns(2)
        with col2a:
            st.header("Equipo 1")
            equipo_A_goles_metidos_seleccion = st.selectbox("Goles a favor", list(range(0,20)), index=int(equipo_A_goles_metidos))
            equipo_A_goles_recibidos_seleccion = st.selectbox("Goles en contra", list(range(0,20)), index=int(equipo_A_goles_recibidos))
            st.data_editor(equipo_A[['jugador','goles_metidos']], hide_index=True, use_container_width=True,
                            column_config ={
                                "jugador": st.column_config.SelectboxColumn(
                                    "Jugador",
                                    options=st.session_state.jugadores['nombre'].sort_values(key=lambda col: col.str.lower())),
                                "goles_metidos":st.column_config.NumberColumn("Goles", default=0, min_value=0, max_value=20, required=True, step='int')
                                    })
            st.write("Suma de goles = " + str(int(equipo_A['goles_metidos'].sum())))
        with col2b:
            st.header("Equipo 2")
            equipo_B_goles_metidos_seleccion = st.selectbox("Goles a favor", list(range(0,20)), index=int(equipo_B_goles_metidos))
            equipo_B_goles_recibidos_seleccion = st.selectbox("Goles en contra", list(range(0,20)), index=int(equipo_B_goles_recibidos))
            st.data_editor(equipo_B[['jugador','goles_metidos']], hide_index=True, use_container_width=True,
                            column_config ={
                                "jugador": st.column_config.SelectboxColumn(
                                    "Jugador",
                                    options=st.session_state.jugadores['nombre'].sort_values(key=lambda col: col.str.lower())),
                                "goles_metidos":st.column_config.NumberColumn("Goles", default=0, min_value=0, max_value=20, required=True, step='int')
                                    })
            st.write("Suma de goles = " + str(int(equipo_B['goles_metidos'].sum())))
        submitted = st.form_submit_button("Guardar")
        if submitted:
            st.write("PENDIENTE: añadir funcion para editar la hoja del GSheet")
with tab2:
    st.header("Configuración")
