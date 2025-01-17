import streamlit as st
import smtplib
import os
from dotenv import load_dotenv
import pymysql
import time
import hashlib
from streamlit_extras.stylable_container import stylable_container
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

#inicializar las variables de entorno
load_dotenv()

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

#funcion para generar contrasena
def generar_contrasena():
    longitud = 8
    mayusculas = string.ascii_uppercase
    minusculas = string.ascii_lowercase
    numeros = string.digits
    #debe tener al menos una mayuscula, una minuscula y un numero
    contrasena = [
        random.choice(mayusculas),
        random.choice(minusculas),
        random.choice(numeros)
    ]
    #completar la contrasena con caracteres aleatorios
    todos_los_caracteres = mayusculas + minusculas + numeros
    contrasena += random.choices(todos_los_caracteres, k=longitud - 3)
    random.shuffle(contrasena)
    return ''.join(contrasena)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    st.markdown("<img src='app/static/squirrel.png' width='100' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)

    st.markdown(
        """
        <h2 style="text-align: center;">Restablece la contraseña</h2>
        """,
        unsafe_allow_html=True
    )

    st.write("Escribe la dirección de correo electrónico o el nombre de usuario vinculados a tu cuenta de QuillaGPT y te enviaremos un mensaje.")

    email = st.text_input(f"**Correo electrónico o nombre de usuario**", placeholder = "Email o nombre de usuario", max_chars = 50)

    flag = ""
    with stylable_container(
        key="registrarse_button",
        css_styles="""
            .element-container:has(#button-after) + div button {
                background-color: #31333F !important;
                color: white !important;
                border-color: #31333F !important;
            }
            .element-container:has(#button-after) + div button::hover {
                background-color: #31333F !important;
                border-color: #31333F !important;
            }
            """,
    ):
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if st.button("Enviar enlace", type = 'secondary', use_container_width = True):
            cursor = conn.cursor()
            query = "SELECT email from User WHERE email = %s OR username = %s"
            values = (email, email)
            cursor.execute(query, values)
            record = cursor.fetchone()
            if record:
                gmail_user = os.getenv("GMAIL_USER")
                gmail_password = os.getenv("GMAIL_PASSWORD")
                sent_from = gmail_user
                sent_to = [record[0]]
                subject = "Restablecimiento de contraseña de QuillaGPT"
                actual_contra = generar_contrasena()
                message = f"""
Estimado usuario,

Esperamos que estés teniendo un excelente día.

Hemos recibido una solicitud para restablecer tu contraseña en QuillaGPT. Para ayudarte a recuperar el acceso a tu cuenta, hemos generado una contraseña temporal:

Contraseña temporal: {actual_contra}

Por tu seguridad, te recomendamos cambiar esta contraseña temporal la primera vez que inicies sesión. Puedes hacerlo desde la sección de "Configuración" en tu perfil.

¡Gracias por confiar en QuillaGPT! Estamos aquí para ayudarte en lo que necesites.

Saludos cordiales,
El equipo de QuillaGPT.
"""
                msg = MIMEMultipart()
                msg['From'] = sent_from
                msg['To'] = ', '.join(sent_to)
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))
                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.ehlo()
                    server.login(gmail_user, gmail_password)
                    server.sendmail(sent_from, sent_to, msg.as_string())
                    cursor = conn.cursor()
                    actual_contra_hasheada = hashlib.sha256(actual_contra.encode()).hexdigest()
                    query = """
                        UPDATE User
                        SET password = %s
                        WHERE email = %s
                        AND active = 1
                    """
                    cursor.execute(query, (actual_contra_hasheada, email))
                    conn.commit()
                    bandera = st.success("Correo enviado con éxito", icon = ":material/check:")
                    time.sleep(4)
                    bandera.empty()
                    st.switch_page("main.py")
                except Exception as e:
                    print(f"Error al enviar el correo: {e}")
                finally:
                    server.close()
            else:
                flag = "El correo electrónico ingresado no se encuentra asociado a una cuenta existente."

    if flag:
        error = st.error(flag)
        time.sleep(4)
        error.empty()