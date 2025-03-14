from fastapi import FastAPI, status
from pydantic import BaseModel
import pymysql
import os
from datetime import datetime
from typing import Optional

def get_db_connection():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )
    return conn

app = FastAPI()

@app.get("/User/{user_email}", status_code = status.HTTP_200_OK)
def get_user_by_email(user_email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = "SELECT * FROM User WHERE email = %s"
    cursor.execute(select_query, (user_email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result
    else:
        return -1
    
class User(BaseModel):
    email: str
    name: str

@app.post("/User", status_code = status.HTTP_201_CREATED)
def create_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = "INSERT INTO User (role_id, email, name, active) VALUES (2, %s, %s, 1)"
    cursor.execute(insert_query, (user.email, user.name))
    conn.commit()
    cursor.close()
    conn.close()
    return user

@app.delete("/Session/{username}", status_code = status.HTTP_200_OK)
def delete_conversations(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    delete_query = """
        UPDATE Session
        SET active = 0
        WHERE user_id = (SELECT user_id FROM User WHERE email = %s)
    """
    cursor.execute(delete_query, (username,))
    conn.commit()
    cursor.close()
    conn.close()
    return username

@app.get("/Session/ObtenerSesionesUsuario/{user_email}", status_code=status.HTTP_200_OK)
def get_sesiones_usuario(user_email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = """
        SELECT title, session_id
        FROM Session s
        JOIN User u ON s.user_id = u.user_id
        WHERE u.email = %s AND s.active = 1
        ORDER BY start_session DESC
    """
    cursor.execute(select_query, (user_email,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.get("/Message/ObtenerMensajesSesion/{session_id}", status_code=status.HTTP_200_OK)
def get_mensajes_sesion(session_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = """
        SELECT role, content
        FROM Message
        WHERE session_id = %s AND active = 1
    """
    cursor.execute(select_query, (session_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

class Session(BaseModel):
    user_id: int
    titulo: str

@app.post("/Session", status_code=status.HTTP_201_CREATED)
def create_session(session: Session):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO Session (start_session, user_id, title, active)
        VALUES (%s, %s, %s, 1)
    """
    cursor.execute(query, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session.user_id, session.titulo))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

class Message(BaseModel):
    session_id: int
    role: str
    content: str
    classification: str

@app.post("/Message", status_code=status.HTTP_201_CREATED)
def create_message(message: Message):
    conn = get_db_connection()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return cursor.lastrowid

class SessionClassification(BaseModel):
    session_id: int
    tema: str

@app.post("/SessionClassification", status_code=status.HTTP_201_CREATED)
def classify_session(session_classification: SessionClassification):
    conn = get_db_connection()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return cursor.lastrowid

class EnviarFeedback(BaseModel):
    derivar: str
    message_id: int
    email: str

@app.post("/RequestQuery", status_code=status.HTTP_201_CREATED)
def request_query(enviar_feedback: EnviarFeedback):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SET SESSION group_concat_max_len = 100000")
    query = """
        INSERT INTO RequestQuery (query, register_date, classification, resolved, user_id, context, active)
        VALUES (%s, %s, (SELECT classification FROM Message WHERE message_id = %s AND active = 1), 0, (SELECT user_id FROM User WHERE email = %s), 
        (
            SELECT GROUP_CONCAT(
                CASE
                    WHEN role = 'user' THEN CONCAT('Usuario: ', content)
                    WHEN role = 'assistant' THEN CONCAT('Asistente: ', content)
                END
                ORDER BY message_id ASC SEPARATOR '\n'
            ) AS formatted_output
            FROM (
                SELECT *
                FROM Message
                WHERE session_id = (
                    SELECT session_id
                    FROM Message
                    WHERE message_id = %s
                )
                AND message_id <= %s
                ORDER BY timestamp DESC
                LIMIT 2
            ) AS last_messages
        ),
        1)
    """
    cursor.execute(query, (enviar_feedback.derivar, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), enviar_feedback.message_id, enviar_feedback.email, enviar_feedback.message_id, enviar_feedback.message_id))
    conn.commit()
    cursor.close()
    conn.close()

class ActualizarDerivado(BaseModel):
    message_id: int
    derivado: int

@app.put("/ActualizarDerivado", status_code=status.HTTP_200_OK)
def actualizar_derivado(actualizar_derivado: ActualizarDerivado):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE Message
        SET derived = %s
        WHERE message_id = %s
        AND active = 1
    """
    cursor.execute(query, (actualizar_derivado.derivado, actualizar_derivado.message_id,))
    conn.commit()
    cursor.close()
    conn.close()

class ActualizarFeedback(BaseModel):
    positivo: int
    message_id: int

@app.put("/ActualizarFeedback", status_code=status.HTTP_200_OK)
def actualizar_feedback(actualizar_feedback: ActualizarFeedback):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE Message
        SET positive = %s
        WHERE message_id = %s
    """
    cursor.execute(query, (actualizar_feedback.positivo, actualizar_feedback.message_id,))
    conn.commit()
    cursor.close()
    conn.close()

class ObtenerUsuarios(BaseModel):
    rol: str
    estado: str
    email: str

@app.get("/ObtenerUsuarios", status_code=status.HTTP_200_OK)
def get_users(usuario: ObtenerUsuarios):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            u.user_id AS 'ID',
            u.name AS 'Nombre de usuario',
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
    cursor.close()
    conn.close()
    return data

class CambiarRolUsuario(BaseModel):
    email: str
    rol: str

@app.put("/User/CambiarRolUsuario", status_code=status.HTTP_200_OK)
def cambiarRolUsuario(usuario: CambiarRolUsuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE User 
        SET role_id = %s 
        WHERE email = %s 
        AND active = 1
    """
    cursor.execute(query, (1 if usuario.rol == "Administrador" else 2, usuario.email))
    conn.commit()
    cursor.close()
    conn.close()

class CargarDocumento(BaseModel):
    contenido: bytes
    filename: str
    current_date: str
    correo: str

@app.post("/CargarDocumento", status_code=status.HTTP_201_CREATED)
def cargar_documento(documento: CargarDocumento):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM User WHERE email = %s", (documento.correo,))
    user = cursor.fetchone()

    query = """
        INSERT INTO File (content, name, register_date, type, active, user_id)
        VALUES (%s, %s, %s, %s, 1, %s)
    """
    cursor.execute(query, (documento.contenido, documento.filename, documento.current_date, 'DocumentoAdicional', user[0]))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid

@app.delete("/File/{file_id}", status_code = status.HTTP_200_OK)
def delete_conversations(file_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    delete_query = """
        DELETE FROM File
        WHERE file_id = %s
    """
    cursor.execute(delete_query, (file_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return 1

@app.get("/File/{document_name}", status_code=status.HTTP_200_OK)
def get_file(document_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = """
        SELECT 
            file_id as 'ID',
            File.name as 'Nombre de documento',
            ROUND(LENGTH(content) / (1024 * 1024), 2) AS 'Tamaño del documento (MB)',
            register_date as 'Fecha de registro',
            u.name as 'Autor del documento'
        FROM File
        INNER JOIN User u ON File.user_id = u.user_id
        WHERE File.active = 1 AND File.name LIKE %s
    """
    cursor.execute(select_query, (f"%{document_name}%",))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.get("/File/", status_code=status.HTTP_200_OK)
def get_file():
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = """
        SELECT 
            file_id as 'ID',
            File.name as 'Nombre de documento',
            ROUND(LENGTH(content) / (1024 * 1024), 2) AS 'Tamaño del documento (MB)',
            register_date as 'Fecha de registro',
            u.name as 'Autor del documento'
        FROM File
        INNER JOIN User u ON File.user_id = u.user_id
        WHERE File.active = 1
    """
    cursor.execute(select_query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.get("/CustomInstruction/", status_code=status.HTTP_200_OK)
def get_custom_instruction():
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = "SELECT instruction FROM CustomInstruction WHERE active = 1"
    cursor.execute(select_query)
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result

@app.get("/ListarInstruccionesInactivas", status_code=status.HTTP_200_OK)
def list_custom_instruction():
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = """
        SELECT instruction, register_date, User.email, User.name
        FROM CustomInstruction
        INNER JOIN User ON CustomInstruction.user_id = User.user_id
        WHERE CustomInstruction.active = 0 
        ORDER BY custom_instruction_id DESC
    """
    cursor.execute(select_query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.put("/ActualizarInstrucciones", status_code=status.HTTP_201_CREATED)
def actualizar_instrucciones():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE CustomInstruction
        SET active = 0
        WHERE active = 1
    """
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

class InsertarInstruccion(BaseModel):
    instruccion: str
    correo: str

@app.post("/CustomInstruction", status_code=status.HTTP_201_CREATED)
def create_custom_instruction(instruction: InsertarInstruccion):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT user_id FROM User WHERE email = %s
    """
    cursor.execute(query, (instruction.correo,))
    user_id = cursor.fetchone()
    query = """
        INSERT INTO CustomInstruction (instruction, register_date, user_id, active)
        VALUES (%s, CURDATE(), %s, 1)
    """
    cursor.execute(query, (instruction.instruccion, user_id[0]))
    conn.commit()
    cursor.close()
    conn.close()

@app.get("/ObtenerClasificaciones", status_code=status.HTTP_200_OK)
def get_request_query_classifications():
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = """
        SELECT classification
        FROM RequestQuery
        WHERE active = 1
        GROUP BY classification
    """
    cursor.execute(select_query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.get("/ObtenerContadorSolicitudes", status_code=status.HTTP_200_OK)
def get_obtener_contador_solicitudes():
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = """
        SELECT COUNT(*)
        FROM RequestQuery
        WHERE active = 1 AND resolved = 0
    """
    cursor.execute(select_query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]

class SolicitudesSoporte(BaseModel):
    tema: str
    estado: str

@app.get("/ObtenerSolicitudesSoporte", status_code=status.HTTP_200_OK)
def get_support_requests(solicitudes_soporte: SolicitudesSoporte):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT request_query_id, register_date, u.email, u.name, classification, query, IF(reply IS NULL, '-', reply), IF(resolved = 1, 'Resuelta', 'Pendiente') AS status
        FROM RequestQuery r
        JOIN User u ON r.user_id = u.user_id
        WHERE r.active = 1 
            AND (%s = 'Todos' OR resolved = %s)
            AND (%s = 'Todos' OR classification = %s)
    """
    cursor.execute(query, (solicitudes_soporte.estado, 1 if solicitudes_soporte.estado == "Resuelta" else 0 if solicitudes_soporte.estado == "Pendiente" else None, solicitudes_soporte.tema, solicitudes_soporte.tema))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

class SolicitudSoporteIndividual(BaseModel):
    indice: int

@app.get("/ObtenerContextoSolicitud", status_code=status.HTTP_200_OK)
def get_support_requests(solicitud: SolicitudSoporteIndividual):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT context
        FROM RequestQuery
        WHERE request_query_id = %s
    """
    cursor.execute(query, (solicitud.indice,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

class SolicitudResolucion(BaseModel):
    respuesta: str
    id: int

@app.put("/SolicitudResolucion", status_code=status.HTTP_201_CREATED)
def request_resolution(solicitud_resolucion: SolicitudResolucion):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE RequestQuery
        SET reply = %s, resolved = 1
        WHERE request_query_id = %s and active = 1
    """
    cursor.execute(query, (solicitud_resolucion.respuesta, solicitud_resolucion.id))
    conn.commit()
    cursor.close()
    conn.close()

class FechasRango(BaseModel):
    start_date: str
    end_date: str

@app.get("/ObtenerCantConversaciones", status_code=status.HTTP_200_OK)
def get_conversations_amount(fechas: FechasRango):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT COUNT(*)
        FROM Session
        WHERE
            start_session >= %s
            AND start_session < DATE_ADD(%s, INTERVAL 1 DAY);
    """
    cursor.execute(query, (fechas.start_date, fechas.end_date))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result

@app.get("/RatioConsultasDerivadas", status_code=status.HTTP_200_OK)
def get_ratio_derived_queries(fechas: FechasRango):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            ROUND((COUNT(CASE WHEN derived = 1 THEN 1 END) * 100.0 / COUNT(*)), 2) AS porcentaje_consultas_derivadas
        FROM 
            Message
        JOIN Session ON Message.session_id = Session.session_id
        WHERE 
            Session.start_session >= %s
            AND Session.start_session < DATE_ADD(%s, INTERVAL 1 DAY) AND role = 'assistant';
    """
    cursor.execute(query, (fechas.start_date, fechas.end_date))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result

@app.get("/PromedioEstudiantesActivos", status_code=status.HTTP_200_OK)
def get_active_students_average(fechas: FechasRango):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            AVG(d.conteo_usuario) AS prom_usuario_activos
        FROM (
            SELECT 
                DATE(start_session) AS dia_interaccion,
                COUNT(DISTINCT Session.user_id) AS conteo_usuario
            FROM 
                Session
            JOIN User ON Session.user_id = User.user_id
            WHERE 
                Session.start_session >= %s
                AND Session.start_session < DATE_ADD(%s, INTERVAL 1 DAY)
                AND User.role_id = 2
            GROUP BY 
                DATE(start_session)
        ) AS d;
    """
    cursor.execute(query, (fechas.start_date, fechas.end_date))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result

@app.get("/CantidadUsuarios", status_code=status.HTTP_200_OK)
def get_users_amount():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT COUNT(*)
        FROM User
        WHERE active = 1
        AND role_id = 2
    """
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result

@app.get("/CantidadConsultasDiarias", status_code=status.HTTP_200_OK)
def get_queries_amount(fechas: FechasRango):
    conn = get_db_connection()
    cursor = conn.cursor()
    # query = """
    #     SELECT 
    #         DATE_FORMAT(register_date, '%%d/%%m/%%Y') AS dia,
    #         COUNT(*) AS conteo_mensajes
    #     FROM Message
    #     JOIN Session ON Message.session_id = Session.session_id
    #     WHERE 
    #         role = 'user'
    #         AND Session.start_session >= %s
    #         AND Session.start_session < DATE_ADD(%s, INTERVAL 1 DAY)
    #     GROUP BY register_date
    #     ORDER BY register_date;
    # """
    query = """
        SELECT 
            register_date as dia,
            COUNT(*) AS conteo_mensajes
        FROM Message
        JOIN Session ON Message.session_id = Session.session_id
        WHERE 
            role = 'user'
            AND Session.start_session >= %s
            AND Session.start_session < DATE_ADD(%s, INTERVAL 1 DAY)
        GROUP BY register_date
        ORDER BY register_date;
    """
    cursor.execute(query, (fechas.start_date, fechas.end_date))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.get("/Top5TemasConsulta", status_code=status.HTTP_200_OK)
def get_top5_query_themes():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            classification AS tema,
            COUNT(*) AS cant_class
        FROM Message
        WHERE active = 1 
            AND role = 'assistant'
            AND classification != 'Otros'
        GROUP BY classification
        ORDER BY cant_class DESC
        LIMIT 5
    """
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result