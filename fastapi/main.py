from fastapi import FastAPI, status
from pydantic import BaseModel
import pymysql
import os
from datetime import datetime

conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)
cursor = conn.cursor()

app = FastAPI()

@app.get("/User/{user_email}", status_code = status.HTTP_200_OK)
def get_user_by_email(user_email: str):
    select_query = "SELECT * FROM User WHERE email = %s"
    cursor.execute(select_query, (user_email,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        return -1
    
class User(BaseModel):
    email: str

@app.post("/User", status_code = status.HTTP_201_CREATED)
def create_user(user: User):
    insert_query = "INSERT INTO User (role_id, email, active) VALUES (2, %s, 1)"
    cursor.execute(insert_query, (user.email,))
    conn.commit()
    return user

@app.delete("/Session/{username}", status_code = status.HTTP_200_OK)
def delete_conversations(username: str):
    delete_query = """
        UPDATE Session
        SET active = 0
        WHERE user_id = (SELECT user_id FROM User WHERE email = %s)
    """
    cursor.execute(delete_query, (username,))
    conn.commit()
    return username

@app.get("/CustomInstruction/", status_code = status.HTTP_200_OK)
def get_custom_instruction():
    select_query = "SELECT instruction FROM CustomInstruction WHERE active = 1"
    cursor.execute(select_query)
    result = cursor.fetchone()[0]
    return result

@app.get("/Session/ObtenerSesionesUsuario/{user_email}", status_code=status.HTTP_200_OK)
def get_sesiones_usuario(user_email: str):
    select_query = """
        SELECT title, session_id
        FROM Session s
        JOIN User u ON s.user_id = u.user_id
        WHERE u.email = %s AND s.active = 1
        ORDER BY start_session DESC
    """
    cursor.execute(select_query, (user_email,))
    result = cursor.fetchall()
    return result

@app.get("/Message/ObtenerMensajesSesion/{session_id}", status_code=status.HTTP_200_OK)
def get_mensajes_sesion(session_id: int):
    select_query = """
        SELECT role, content
        FROM Message
        WHERE session_id = %s AND active = 1
    """
    cursor.execute(select_query, (session_id,))
    result = cursor.fetchall()
    return result

class Session(BaseModel):
    user_id: int
    titulo: str

@app.post("/Session", status_code=status.HTTP_201_CREATED)
def create_session(session: Session):
    query = """
        INSERT INTO Session (start_session, user_id, title, active)
        VALUES (%s, %s, %s, 1)
    """
    cursor.execute(query, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session.user_id, session.titulo))
    conn.commit()
    return cursor.lastrowid

class Message(BaseModel):
    session_id: int
    role: str
    content: str
    classification: str

@app.post("/Message", status_code=status.HTTP_201_CREATED)
def create_message(message: Message):
    if message.classification == "-1":
        query = """
            INSERT INTO Message (session_id, timestamp, register_date, role, content, active)
            VALUES (%s, %s, %s, %s, %s, 1)
        """
        cursor.execute(query, (message.session_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%y-%m-%d'), message.role, message.content))
    else:
        query = """
            INSERT INTO Message (session_id, timestamp, register_date, role, content, classification, active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """
        cursor.execute(query, (message.session_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%y-%m-%d'), message.role, message.content, message.classification))
    conn.commit()
    return cursor.lastrowid

class SessionClassification(BaseModel):
    session_id: int
    tema: str

@app.post("/SessionClassification", status_code=status.HTTP_201_CREATED)
def classify_session(session_classification: SessionClassification):
    query = """
        INSERT INTO SessionClassification (timestamp, session_id, classification, active)
        VALUES (%s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE timestamp = %s
    """
    cursor.execute(
        query,
        (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            session_classification.session_id,
            session_classification.tema,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    )
    conn.commit()
    return cursor.lastrowid

class EnviarFeedback(BaseModel):
    derivar: str
    message_id: int
    email: str

@app.post("/RequestQuery", status_code=status.HTTP_201_CREATED)
def request_query(enviar_feedback: EnviarFeedback):
    query = """
        INSERT INTO RequestQuery (query, register_date, classification, resolved, user_id, active)
        VALUES (%s, %s, (SELECT classification FROM Message WHERE message_id = %s AND active = 1), 0, (SELECT user_id FROM User WHERE email = %s), 1)
    """
    cursor.execute(query, (enviar_feedback.derivar, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), enviar_feedback.message_id, enviar_feedback.email))
    conn.commit()

class ActualizarDerivado(BaseModel):
    message_id: int
    derivado: int

@app.put("/ActualizarDerivado", status_code=status.HTTP_200_OK)
def actualizar_derivado(actualizar_derivado: ActualizarDerivado):
    query = """
        UPDATE Message
        SET derived = %s
        WHERE message_id = %s
        AND active = 1
    """
    cursor.execute(query, (actualizar_derivado.derivado, actualizar_derivado.message_id,))
    conn.commit()

class ActualizarFeedback(BaseModel):
    positivo: int
    message_id: int

@app.put("/ActualizarFeedback", status_code=status.HTTP_200_OK)
def actualizar_feedback(actualizar_feedback: ActualizarFeedback):
    query = """
        UPDATE Message
        SET positive = %s
        WHERE message_id = %s
    """
    cursor.execute(query, (actualizar_feedback.positivo, actualizar_feedback.message_id,))
    conn.commit()

class ObtenerUsuarios(BaseModel):
    rol: str
    estado: str
    email: str

@app.get("/ObtenerUsuarios", status_code=status.HTTP_200_OK)
def get_users(usuario: ObtenerUsuarios):
    query = """
        SELECT 
            u.user_id AS 'ID',
            u.email AS 'Correo electrónico', 
            r.name AS 'Rol', 
            CASE WHEN u.active = 1 THEN 'Activo' ELSE 'Inactivo' END AS 'Estado'
        FROM User u
        INNER JOIN Role r ON u.role_id = r.role_id
        WHERE (%s = 'Todos' OR r.name = %s)
        AND (%s = 'Todos' OR u.active = %s)
        AND (%s = '' OR u.email LIKE %s)
        ORDER BY u.user_id
    """
    values = (
        usuario.rol, usuario.rol, 
        usuario.estado, 1 if usuario.estado == 'Activo' else 0 if usuario.estado == 'Inactivo' else None,
        usuario.email, f"%{usuario.email}%"
    )
    cursor.execute(query, values)
    data = cursor.fetchall()
    return data

class CambiarRolUsuario(BaseModel):
    email: str
    rol: str

@app.put("/User/CambiarRolUsuario", status_code=status.HTTP_200_OK)
def cambiarRolUsuario(usuario: CambiarRolUsuario):
    query = """
        UPDATE User 
        SET role_id = %s 
        WHERE email = %s 
        AND active = 1
    """
    cursor.execute(query, (1 if usuario.rol == "Administrador" else 2, usuario.email))
    conn.commit()