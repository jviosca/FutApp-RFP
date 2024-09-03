import pandas as pd
import datetime
import random
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import sys

def create_gsheets_connection():
    # Create a gsheets connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn

def leer_gsheets(conn, ttl="10m"):
    
    temporadas = conn.read(worksheet="temporadas", ttl=ttl)
    partidos = conn.read(worksheet="registro_partidos", ttl=ttl)
    jugadores = conn.read(worksheet="jugadores", ttl=ttl)
    mvp = conn.read(worksheet="MVP", ttl=ttl)
    return temporadas,partidos,jugadores,mvp

def clasificacion(partidos,jugadores, mvp, jornada='todas', umbral_goles_recibidos = 4):
    ''' Devuelve una tabla (dataframe) con la clasificacion y metricas de interes incluyendo todas las jornadas
    hasta la indicada (acumulativo)
    La clasificacion se basa en la puntuacion. En cada jornada, un jugador puede obtener hasta 4 puntos:
    - 1 punto por asistir.
    - 1 punto por ganar el partido
    - 1 punto por ser el máximo goleador. Si hay 2 (o +) jugadores que han metido la máxima cantidad de goles, todos 
    ellos se llevan 1 punto. 
    - 1 punto por lograr que el equipo reciba menos goles que el umbral_goles_recibidos
    - 1 punto si eres portero y tu equipo recibe menos goles que el umbral_goles_recibidos
    
    INPUT:
        partidos (dataframe)
        jugadores (datadframe)
        jornada (int o 'todas'): numero jornada para calcular clasificacion. Si es 'todas' incluye todas
        umbral_goles_recibidos (int): por defecto es 4. 4 o menos goles, entonces el equipo ha defendido bien
    OUTPUT:
        clasificacion (dataframe), con las columnas:
            - Posición: de 1 a 27
            - Jugador: nombre del jugador
            - Puntos: acumulativo de todas las jornadas hasta la fecha. En paréntesis: los puntos conseguidos en la última jornada.
            - Goles: acumulativo. En paréntesis: los goles en la última jornada.
            - Jugados: acumulativo hasta la fecha
            - Ganados: acumulativo hasta la fecha
        '''
    
    if jornada == 'todas':
        lista_jornadas = partidos['jornada'].dropna().unique()
        lista_jornadas = sorted(lista_jornadas)
    else:
        lista_jornadas = range(1,jornada + 1)
    # quitamos ultima jornada si no tiene jugadores
    if partidos.loc[partidos['jornada']==lista_jornadas[-1]]['jugador'].dropna().shape[0] == 0:
        lista_jornadas.remove(lista_jornadas[-1])
    # guardamos una lista con porteros
    lista_porteros = jugadores.loc[jugadores['posicion']=='portero']['nombre'].values
    # guardamos los valores de interes en listas dentro de diccionarios
    dict_fechas_jornadas = {}
    dict_maximos_goleadores_jornadas = {}
    dict_pocos_goleados_jornadas = {}
    dict_partidos_ganados_jornadas = {}
    dict_partidos_jugados_jornadas = {}
    dict_mvp_jornadas = {}
    dict__msg_mvp_jornadas = {}
    
    for jornada in lista_jornadas:
        #print("Jornada " + str(jornada))
        df_jornada = partidos.loc[partidos['jornada']==jornada]
        dict_fechas_jornadas[jornada] = df_jornada['fecha'].dropna().head(1).values[0]
        maximos_goleadores_lista = df_jornada.loc[df_jornada['goles_metidos'] == df_jornada['goles_metidos'].max()]['jugador'].tolist()
        #print(maximos_goleadores_lista)
        dict_maximos_goleadores_jornadas[jornada] = maximos_goleadores_lista
        minimos_goles_encajados_lista = df_jornada.loc[df_jornada['goles_recibidos'] <= umbral_goles_recibidos]['jugador'].tolist()
        dict_pocos_goleados_jornadas[jornada] = minimos_goles_encajados_lista
        ganadores_lista = df_jornada.loc[df_jornada['resultado_partido'] == 'Ganado']['jugador'].tolist()
        dict_partidos_ganados_jornadas[jornada] = ganadores_lista
        jugadores_jornada_lista = df_jornada['jugador'].tolist()
        #st.write(jugadores_jornada_lista)
        dict_partidos_jugados_jornadas[jornada] = jugadores_jornada_lista 
        mvp['jornada_n'] = mvp['Jornada'].apply(lambda x: int(x.split('Jornada ')[1].split('|')[0][:-1]))
        mvp.drop_duplicates(['Dirección de correo electrónico','jornada_n'], keep='last', inplace=True)
        emails_jugadores_jornada = jugadores.loc[jugadores['nombre'].isin(partidos.loc[partidos['jornada']==jornada]['jugador'])]['email']
        df_elegidos_mvp = mvp.loc[(mvp['jornada_n']==jornada) & (mvp['Dirección de correo electrónico'].isin(emails_jugadores_jornada)) & (mvp['Mejor jugador del partido'].isin(jugadores_jornada_lista))]
        dict_mvp_jornadas[jornada] = None
        dict__msg_mvp_jornadas[jornada] = None
        fecha_partido = datetime.datetime.strptime(dict_fechas_jornadas[jornada],'%d/%m/%Y')
        fecha_cierre_mvp = fecha_partido + datetime.timedelta(days=3)
        if datetime.datetime.today() >= fecha_cierre_mvp:
            if df_elegidos_mvp.shape[0] >= 7:
                elegidos_mvp = df_elegidos_mvp['Mejor jugador del partido'].mode().values
                if len(elegidos_mvp) == 1:
                    dict_mvp_jornadas[jornada] = elegidos_mvp[0]
                else:
                    dict__msg_mvp_jornadas[jornada] = "*En la votación del MPV de la jornada " + str(int(jornada)) + " ha habido un empate entre " + ' y '.join(jugador for jugador in elegidos_mvp) + ", por lo que no se ha repartido este punto.*"
            else:
                dict__msg_mvp_jornadas[jornada] = "*En la votación del MPV de la jornada " + str(int(jornada)) + " no ha habido al menos 7 votos, por lo que no se ha repartido este punto.*"
        else:
            dict__msg_mvp_jornadas[jornada] = "*La votación del MVP está en curso. Se han recibido " + str(df_elegidos_mvp.shape[0]) + " votaciones*"
    #print(dict_mvp_jornadas[jornada])
    #st.write(dict_mvp_jornadas)

    # ahora guardamos puntos en un dataframe
    clasificacion_df = pd.DataFrame(columns=['Jugador','puntos_0', 'Puntos','Goles','Jugados','Ganados'])
    clasificacion_df.set_index('Jugador',inplace=True)
    lista_jugadores_todos = jugadores['nombre'].dropna()
    for jugador in lista_jugadores_todos:
        puntos_0 = 0
        puntos = 0
        jugados_0 = 0
        jugados = 0
        ganados_0 = 0
        ganados = 0
        for jornada in lista_jornadas:
            if jugador in dict_maximos_goleadores_jornadas[jornada]:
                puntos = puntos + 1
            if jugador in dict_pocos_goleados_jornadas[jornada]:
                puntos = puntos + 1    
                if jugador in lista_porteros:
                    puntos = puntos + 1
            if jugador in dict_partidos_ganados_jornadas[jornada]:
                puntos = puntos + 1
                ganados = ganados + 1
            if jugador in dict_partidos_jugados_jornadas[jornada]:
                puntos = puntos + 1
                jugados = jugados + 1
            
            if dict_mvp_jornadas[jornada] != None:
                if jugador == dict_mvp_jornadas[jornada]:
                    puntos = puntos + 1
            
            # calculamos cambio con semana anterior
            if jornada > 1:
                if jugador in dict_maximos_goleadores_jornadas[jornada-1]: 
                    puntos_0 = puntos_0 + 1
                if jugador in dict_pocos_goleados_jornadas[jornada-1]:
                    puntos_0 = puntos_0 + 1       
                    if jugador in lista_porteros:
                        puntos_0 = puntos_0 + 1
                if jugador in dict_partidos_ganados_jornadas[jornada-1]:
                    puntos_0 = puntos_0 + 1
                    ganados_0 = ganados_0 + 1
                if jugador in dict_partidos_jugados_jornadas[jornada-1]:
                    puntos_0 = puntos_0 + 1 
                    jugados_0 = jugados_0 + 1
                if dict_mvp_jornadas[jornada-1] != None:
                    if jugador == dict_mvp_jornadas[jornada-1]:
                        puntos_0 = puntos_0 + 1 
                        #print(jornada)
                        #print(dict_mvp_jornadas[jornada-1])
                    
            goles_ultima_jornada = partidos.loc[(partidos['jugador']==jugador) & (partidos['jornada']==jornada)]['goles_metidos'].values
            if len(goles_ultima_jornada)>0:
                goles_ultima_jornada = goles_ultima_jornada[0]
            else:
                goles_ultima_jornada = 0
            #print(goles_ultima_jornada)
        clasificacion_df.loc[jugador,'puntos'] = puntos
        #clasificacion.loc[jugador,'puntos'] = puntos
        # guardamos puntos jornada anterior para cambio en posicion
        clasificacion_df.loc[jugador,'puntos_0'] = puntos_0
        
        if puntos == puntos_0:
            clasificacion_df.loc[jugador,'Puntos'] = str(puntos) + " (=)"
        elif puntos > puntos_0:
            clasificacion_df.loc[jugador,'Puntos'] = str(puntos) + " (+" + str(puntos-puntos_0) + ")"
        
        clasificacion_df.loc[jugador,'Jugados'] = jugados
        clasificacion_df.loc[jugador,'jugados_0'] = jugados_0
        clasificacion_df.loc[jugador,'Ganados'] = ganados
        clasificacion_df.loc[jugador,'ganados_0'] = ganados_0
        # guardamos los goles
        goles_total = partidos.loc[partidos['jugador']==jugador]['goles_metidos'].sum()
        '''
        if len(goles_total)>0:
            goles_total = str(goles_total[0])
        else:
            goles_total = str(0)
        '''
        if goles_ultima_jornada == 0:
            clasificacion_df.loc[jugador,'Goles'] = str(int(goles_total)) + " (=)"
            clasificacion_df.loc[jugador,'goles'] = goles_total
            clasificacion_df.loc[jugador,'goles_0'] = goles_total
        else:
            clasificacion_df.loc[jugador,'Goles'] = str(int(goles_total)) + " (+" + str(int(goles_ultima_jornada)) + ")"
            clasificacion_df.loc[jugador,'goles'] = goles_total
            clasificacion_df.loc[jugador,'goles_0'] = goles_total - goles_ultima_jornada     
    #st.write("Clasificación hasta la jornada " + str(int(list(dict_fechas_jornadas.keys())[-1])) + " (" + pd.to_datetime(dict_fechas_jornadas[list(dict_fechas_jornadas)[-1]], dayfirst=True, format="%d/%m/%Y")[0].strftime("%d/%m/%Y") + ")")
    st.write("Clasificación hasta la jornada " + str(int(list(dict_fechas_jornadas.keys())[-1])) + " (" + dict_fechas_jornadas[list(dict_fechas_jornadas)[-1]] + ")")
    st.write("Jugar: +1; Ganar: +1; Max goleador: +1;\n<5 goles: +1 [portero: +1]; MVP (🌟): +1")
    if dict__msg_mvp_jornadas[max(dict__msg_mvp_jornadas)] != None:
        st.write(dict__msg_mvp_jornadas[max(dict__msg_mvp_jornadas)])
    clasificacion_df.reset_index(inplace=True)
    # calculamos posicion jornada anterior
    clasificacion_df.sort_values(['puntos_0','jugados_0','ganados_0','Goles'], ascending=False, inplace=True)
    clasificacion_df['posicion_jornada_anterior'] = [pos+1 for pos,item in enumerate(clasificacion_df.sort_values(['puntos_0','jugados_0','ganados_0','goles_0'], ascending=False)['Jugador'].tolist())]
    clasificacion_df.sort_values(['puntos','Jugados','Ganados','goles'], ascending=False, inplace=True)
    clasificacion_df['posicion'] = range(1,clasificacion_df.shape[0]+1)
    pos_jornada_anterior = clasificacion_df['posicion_jornada_anterior'].tolist()
    pos_jornada_ultima = clasificacion_df['posicion'].tolist()
    pos_ultima_con_cambio = []
    for ultima,anterior in zip(pos_jornada_ultima,pos_jornada_anterior):
        if len(lista_jornadas) > 1: # solo ponemos marca de cambio si es jornada >=2
            if ultima == anterior:
                pos_ultima_con_cambio.append(str(ultima) + ' =')
            elif ultima < anterior:
                pos_ultima_con_cambio.append(str(ultima) + ' ↑')
            else:
                pos_ultima_con_cambio.append(str(ultima) + ' ↓')
        else: # si es jornada 1, no ponemos marca de cambio
            pos_ultima_con_cambio.append(str(ultima))
    clasificacion_df['Posición'] = pos_ultima_con_cambio
    clasificacion_df.set_index('Posición', inplace=True)
    clasificacion_df.drop(columns=['puntos_0','puntos','posicion', 'posicion_jornada_anterior', 'jugados_0','ganados_0','goles','goles_0'], inplace=True)
    # añadimos estrella al MVP
    print(dict_mvp_jornadas[max(dict_fechas_jornadas)])
    if dict_mvp_jornadas[max(dict_fechas_jornadas)] != None:
        clasificacion_df['Jugador'] = clasificacion_df['Jugador'].apply(lambda x: '🌟 ' + x if x == dict_mvp_jornadas[max(dict_fechas_jornadas)] else x)
    return clasificacion_df
