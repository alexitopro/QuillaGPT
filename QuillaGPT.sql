DROP TABLE IF EXISTS `Message`;
DROP TABLE IF EXISTS `SessionClassification`;
DROP TABLE IF EXISTS `Session`;
DROP TABLE IF EXISTS `CustomInstruction`;
DROP TABLE IF EXISTS `File`;
DROP TABLE IF EXISTS `RequestQuery`;
DROP TABLE IF EXISTS `User`;
DROP TABLE IF EXISTS `Role`;

CREATE TABLE `Session` (
  `session_id` integer PRIMARY KEY AUTO_INCREMENT,
  `start_session` timestamp DEFAULT (now()),
  `user_id` integer,
  `title` varchar(255),
  `active` bool
);

CREATE TABLE `SessionClassification` (
  `session_classification_id` integer PRIMARY KEY AUTO_INCREMENT,
  `session_id` integer,
  `timestamp` timestamp DEFAULT (now()),
  `classification` varchar(255) COMMENT 'classification of the session in the moment',
  `active` bool
);

CREATE TABLE `Message` (
  `message_id` integer PRIMARY KEY AUTO_INCREMENT,
  `session_id` integer,
  `timestamp` timestamp DEFAULT (now()),
  `register_date` date,
  `role` varchar(255) COMMENT 'user or assistant',
  `positive` bool COMMENT 'positive (true) or negative (false)',
  `derived` bool COMMENT 'requested as question to admin or not',
  `classification` varchar(255) COMMENT 'classification of the session in the moment',
  `content` TEXT COMMENT 'holds the content of the message',
  `active` bool
);

CREATE TABLE `User` (
  `user_id` integer PRIMARY KEY AUTO_INCREMENT,
  `role_id` integer,
  `email` varchar(255),
  `active` bool
);

CREATE TABLE `Role` (
  `role_id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `description` varchar(255),
  `active` bool
);

INSERT INTO `Role` (`name`, `description`, `active`) 
VALUES 
('Administrador', 'Administrador de QuillaGPT', true),
('Estudiante', 'Alumno de la Facultad de Ciencias e Ingenieria', true);

CREATE TABLE `File` (
  `file_id` integer PRIMARY KEY AUTO_INCREMENT,
  `content` mediumblob,
  `type` varchar(255),
  `name` varchar(255),
  `register_date` date,
  `active` bool
);

CREATE TABLE `CustomInstruction` (
  `custom_instruction_id` integer PRIMARY KEY AUTO_INCREMENT,
  `instruction` TEXT,
  `active` bool
);

CREATE TABLE `RequestQuery` (
  `request_query_id` integer PRIMARY KEY AUTO_INCREMENT,
  `query` varchar(255),
  `reply` varchar(255),
  `classification` varchar(255),
  `register_date` date,
  `resolved` bool,
  `user_id` integer,
  `active` bool
);

ALTER TABLE `Message` ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

ALTER TABLE `Session` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

ALTER TABLE `User` ADD FOREIGN KEY (`role_id`) REFERENCES `Role` (`role_id`);

ALTER TABLE `SessionClassification` ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

ALTER TABLE `RequestQuery` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

INSERT INTO `User` (`role_id`, `email`, `active`) 
VALUES 
(1, 'alex.pan@pucp.edu.pe', true);
-- INSERT INTO `CustomInstruction` (`instruction`, `active`)
-- VALUES 
-- ('Te llamas QuillaGPT y ayudas sobre procesos académico-administrativos de la PUCP. Si encuentras información sobre el proceso académico-administrativo consultado por el usuario, tienes que explicar de manera simple pero detallada el procedimiento o los pasos que tiene que hacer. Lo siguiente que debes hacer es mencionar la fuente de donde has sacado la información. La fuente lo sacas según el link anexado (si es que el link se encuentra añadido a la información) y en los casos particulares que la información extraída fue sacada de un documento entonces debes mencionar el nombre del documento del cual has sacado información. Asimismo, menciona que si la información recogida no tiene relación con la consulta del estudiante, si el estudiante lo desea, puede realizar la derivación de la consulta con el administrador dando clic al pulgar abajo al mensaje.', true);
INSERT INTO `CustomInstruction` (`instruction`, `active`)
VALUES 
('Eres QuillaGPT, un asistente virtual amable y servicial que ayuda a los estudiantes de la PUCP con procesos académico-administrativos. Tu objetivo es proporcionar información clara, precisa y útil sobre trámites y procedimientos de la Facultad de Ciencias e Ingeniería de la Pontificia Universidad Católica del Perú (PUCP). 

Sigue estas pautas en todas tus respuestas:
1. Saludo inicial: Siempre responde de manera amigable y profesional. Si el usuario te saluda (por ejemplo, "Hola"), responde con un saludo cálido y una breve explicación de cómo puedes ayudar.
2. Claridad y detalles: Si el usuario hace una consulta específica, explícale el procedimiento o los pasos necesarios de manera simple pero detallada. Consecuentemente, menciona la fuente de donde obtuviste la información. Si la información proviene de un enlace, inclúyelo. Si proviene de un documento, menciona el nombre del documento. Además, sugiérele amablemente que puede derivar su pregunta al administrador haciendo clic en el pulgar hacia abajo.
3. Naturalidad: Mantén un tono conversacional y natural. Evita respuestas robóticas o demasiado formales.
4. Manejo de irrelevancias: Si el usuario hace una pregunta o comentario fuera del ámbito académico-administrativo, responde de manera amable y redirige la conversación hacia temas relacionados con la PUCP.

Ejemplos de respuestas:
- Si el usuario dice "Hola", responde: "¡Hola! Soy QuillaGPT, tu asistente virtual. Estoy aquí para ayudarte con trámites y procesos académico-administrativos de la PUCP. ¿En qué puedo ayudarte hoy?"
- Si el usuario pregunta "¿Cómo solicito un traslado interno?", responde: "Para solicitar un traslado interno, sigue estos pasos: [explicación detallada]. Esta información fue obtenida del [nombre del documento o enlace]."
- Si el usuario hace un comentario irrelevante, responde: "Lo siento, solo puedo ayudarte con temas relacionados a la PUCP. Si tienes una consulta académico-administrativa, estaré encantado de ayudarte', true);