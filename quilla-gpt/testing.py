# import streamlit as st
# import pymysql
# import hashlib
# import time
# import pandas as pd
# import numpy as np
# from st_aggrid import AgGrid, GridOptionsBuilder

# st.set_page_config(
#     layout = "wide",
#     page_title = "QuillaGPT"
# )

# #conexion en mysql
# conn = pymysql.connect(
#     host=st.secrets["mysql"]["host"],
#     user=st.secrets["mysql"]["username"],
#     password=st.secrets["mysql"]["password"],
#     database=st.secrets["mysql"]["database"]
# )

# #crear la variable de ID tabla para poder reiniciar la seleccion
# if "tabla_id" not in st.session_state:
#     st.session_state.tabla_id = 0

# #modal para revisar la consulta del estudiante
# @st.dialog("Detalle de la consulta")
# def verDetalle(parameter):

#     st.text_input("**Tema**", value=parameter, disabled=True)

#     if st.button("Cerrar"):
#         st.session_state.tabla_id +=1
#         st.rerun()

# if "df" not in st.session_state:
#     st.session_state.df = pd.DataFrame(
#         np.random.randn(12, 5), columns=["a", "b", "c", "d", "e"]
#     )

# df = st.session_state.df

# event = st.dataframe(
#     st.session_state.df,
#     on_select="rerun",
#     selection_mode=["single-row"],
#     hide_index=True,
#     key = str(st.session_state.tabla_id)
# )

# if event.selection is not None:
#     if event.selection['rows']:
#         selected_index = event.selection['rows'][0]  # Get the index of the first selected row
#         value_a = df.loc[selected_index, 'a']  # Access the value in column 'a' for the selected row
#         verDetalle(value_a)
#     # st.write(event.selection.rows)
#     # st.write(f"Value of column 'a' in the selected row: {value_a}")

import streamlit as st
import pymysql
import hashlib
import time
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#conexion en mysql
conn = pymysql.connect(
    host=st.secrets["mysql"]["host"],
    user=st.secrets["mysql"]["username"],
    password=st.secrets["mysql"]["password"],
    database=st.secrets["mysql"]["database"]
)

#crear la variable de ID tabla para poder reiniciar la seleccion
if "tabla_id" not in st.session_state:
    st.session_state.tabla_id = 0

#modal para revisar la consulta del estudiante
@st.dialog("Detalle de la consulta")
def verDetalle(selected_index):

    st.text_input("**Tema**", value=df.loc[selected_index, "Tema"], disabled=True)

    st.text_area("**Consulta del estudiante**", value=df.loc[selected_index, "Consulta"], disabled=True)

    if df.loc[selected_index, "Estado"] == "Resuelta":
        respuesta = st.text_area("**Respuesta**", value=df.loc[selected_index, "Respuesta"], disabled = True)
    else:
        respuesta = st.text_area("**Respuesta**", placeholder="Ingrese la respuesta a la consulta...")
        col1, col2 = st.columns([4, 2])
        with col2:
            if st.button("Guardar cambios", type="primary"):
                cursor = conn.cursor()
                query = """
                    UPDATE RequestQuery
                    SET reply = %s, resolved = 1
                    WHERE request_query_id = %s and active = 1
                """
                cursor.execute(query, (respuesta, df.loc[selected_index, "ID"]))
                conn.commit()
                st.session_state.tabla_id += 1
                st.rerun()

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Banco de Consultas")

cursor = conn.cursor()
query = """
    SELECT request_query_id, register_date, classification, query, IF(reply IS NULL, '-', reply), IF(resolved = 1, 'Resuelta', 'Pendiente') AS status
    FROM RequestQuery
    WHERE active = 1
"""
cursor.execute(query)
data = cursor.fetchall()
df = pd.DataFrame(data, columns=["ID", "Fecha de registro", "Tema", "Consulta", "Respuesta", "Estado"])
df['Fecha de registro'] = pd.to_datetime(df['Fecha de registro'], format="%d/%m/%Y")

event = st.dataframe(
    df,
    on_select="rerun",
    selection_mode=["single-row"],
    hide_index=True,
    key = str(st.session_state.tabla_id)
)

if event.selection is not None:
    if event.selection['rows']:
        selected_index = event.selection['rows'][0]
        # value_a = df.loc[selected_index, 'a']
        verDetalle(selected_index)