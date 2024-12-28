import streamlit_authenticator as stauth
import streamlit as st

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#settings for text input
tabs_font_css = """
<style>
div[class*="forgot_password"] p {
    text-decoration: underline;
}
div[class*="register"] p {
    text-decoration: underline;
}
# </style>
# """
st.write(tabs_font_css, unsafe_allow_html=True)
#settings for input
# st.markdown(
#     """
#     <style>
#         input {
#             font-size: 15px !important;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

st.markdown("<img src='app/static/squirrel.png' width='150' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)
st.markdown(
    """
    <h2 style="text-align: center;">Inicia sesión en QuillaGPT</h2>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    username = st.text_input(f"**Correo electrónico**", placeholder = "Email", max_chars = 50)

    password = st.text_input(f"**Contraseña**", placeholder = "Contraseña", type = "password", max_chars = 50)

    if st.button("Iniciar sesión", type = 'primary', use_container_width = True):
        st.toast("Iniciando sesión...")
        
    if st.button("¿Has olvidado tu contraseña?", type = "tertiary", use_container_width = True, key = "forgot_password"):
        st.toast("Enviando correo de recuperación...")

    if st.button("¿No tienes cuenta? Regístrate en QuillaGPT", type = "tertiary", use_container_width = True, key = "register"):
        st.toast("Redirigiendo a la página de registro...")