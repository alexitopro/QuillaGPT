import streamlit as st

def send_feedback(derivar):
  cursor = conn.cursor()
  query = """
    INSERT INTO RequestQuery (query, register_date, classification, resolved, active)
    VALUES (%s, %s, (SELECT classification FROM Message WHERE message_id = %s), 0, 1)
  """
  cursor.execute(query, (derivar, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), st.session_state.message_response_id))
  conn.commit()
  
@st.dialog("¿La respuesta brindada no fue de tu satisfacción?")
def config_feedback(message_id):
  st.write("Si QuillaGPT no ha podido responder a tu consulta y deseas que fuera respondida, favor de indicarlo en el recuadro de abajo para derivar la consulta al administrador.")
  derivar = st.text_area("**Consulta a derivar al administrador**", height=250, max_chars=500, placeholder="Escribe aquí tu consulta...")
  col1, col2, col3 = st.columns([5, 2, 2])
  with col2:
    if st.button("Cancelar", type="secondary", use_container_width=True):
        st.rerun()
  with col3:
    if st.button("Enviar", type="primary", use_container_width=True, args=(derivar, ), on_click=send_feedback):
        st.rerun()
        


if st.button("Enviar enlace", type = 'secondary', use_container_width = True):
    config_feedback()