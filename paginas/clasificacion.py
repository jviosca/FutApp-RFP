import streamlit as st
import datetime
import aux_functions as aux

                
st.title("New Real Patata FutApp")          
st.header("Clasificación")          
temporadas,partidos,jugadores,mvp = aux.leer_gsheets(aux.create_gsheets_connection())
temporada_elegida_años = st.selectbox("Escoge temporada",temporadas['nombre'], index=len(temporadas['nombre'])-1)
temporada_elegida_n = temporadas.loc[temporadas['nombre']==temporada_elegida_años]['numero'].values[0]
# filtramos la temporada
mvp['temporada_n'] = mvp['Jornada'].apply(lambda x: int(x.split('Temporada ')[1][:-1]))
mvp_temporada_elegida = mvp.loc[mvp['temporada_n']==temporada_elegida_n]
partidos_temporada_elegida = partidos.loc[partidos['temporada']==temporada_elegida_n]
#st.dataframe(partidos_temporada_elegida)
if partidos_temporada_elegida.shape[0] > 0:
    fecha_ultimo_partido = datetime.datetime.strptime(partidos.dropna(subset='jugador').iloc[-1]['fecha'],'%d/%m/%Y')
    fecha_cierre_mvp = fecha_ultimo_partido + datetime.timedelta(days=3)
    #st.write(fecha_ultimo_partido)
    if datetime.datetime.today() < fecha_cierre_mvp and datetime.datetime.today() > fecha_ultimo_partido:
        st.markdown("**Esta clasificación es temporal y está pendiente de la votación del MVP. La fecha límite para la votación es el jueves a las 23:59. A partir del viernes, la clasificación será definitiva**")
    try:
        clasificacion_df = aux.clasificacion(partidos_temporada_elegida,jugadores,mvp_temporada_elegida)
        st.table(clasificacion_df)
        #st.data_editor(clasificacion_df, disabled=True, use_container_width=True, height=980)
    except:
        st.write("Todavía no se han introducido los goles de ningún partido")
        pass
else:
    st.write("No hay partidos en la temporada elegida")
