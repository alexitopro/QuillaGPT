-- Active: 1735456594891@@localhost@3306@pandagpt
DROP TABLE IF EXISTS `Message`;

DROP TABLE IF EXISTS `RequestQuery`;

DROP TABLE IF EXISTS `SessionClassification`;

DROP TABLE IF EXISTS `Session`;

DROP TABLE IF EXISTS `CustomInstruction`;

DROP TABLE IF EXISTS `File`;

DROP TABLE IF EXISTS `User`;

DROP TABLE IF EXISTS `Role`;

-- CREATE TABLE `Session` (
--   `session_id` integer PRIMARY KEY AUTO_INCREMENT,
--   `start_session` timestamp DEFAULT (now()),
--   `user_id` integer,
--   `title` varchar(255),
--   `active` bool
-- );

-- CREATE TABLE `SessionClassification` (
--   `session_classification_id` integer PRIMARY KEY AUTO_INCREMENT,
--   `session_id` integer,
--   `timestamp` timestamp DEFAULT (now()),
--   `classification` varchar(255) COMMENT 'classification of the session in the moment',
--   `active` bool
-- );

CREATE TABLE `Session` (
    `session_id` integer PRIMARY KEY AUTO_INCREMENT,
    `start_session` timestamp DEFAULT(now()),
    `title` varchar(255),
    `user_id` integer,
    `created_at` date DEFAULT(now()),
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `active` bool
);

CREATE TABLE `SessionClassification` (
    `session_classification_id` integer PRIMARY KEY AUTO_INCREMENT,
    `session_id` integer,
    `timestamp` timestamp DEFAULT(now()),
    `classification` varchar(255) COMMENT 'classification of the session in the moment',
    `created_at` date DEFAULT(now()),
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `active` bool
);

CREATE TABLE `Message` (
    `message_id` integer PRIMARY KEY AUTO_INCREMENT,
    `session_id` integer,
    `timestamp` timestamp DEFAULT(now()),
    `register_date` date,
    `role` varchar(255) COMMENT 'user or assistant',
    `positive` bool COMMENT 'positive (true) or negative (false)',
    `derived` bool COMMENT 'requested as question to admin or not',
    `classification` varchar(255) COMMENT 'classification of the session in the moment',
    `content` TEXT COMMENT 'holds the content of the message',
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `active` bool
);

-- CREATE TABLE `User` (
--   `user_id` integer PRIMARY KEY AUTO_INCREMENT,
--   `name` varchar(255),
--   `role_id` integer,
--   `email` varchar(255),
--   `active` bool
-- );

CREATE TABLE `User` (
    `user_id` integer PRIMARY KEY AUTO_INCREMENT,
    `name` varchar(255),
    `role_id` integer,
    `email` varchar(255),
    `created_at` date DEFAULT(now()),
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `active` bool
);

CREATE TABLE `Role` (
    `role_id` integer PRIMARY KEY AUTO_INCREMENT,
    `name` varchar(255),
    `description` varchar(255),
    `active` bool
);

INSERT INTO
    `Role` (
        `name`,
        `description`,
        `active`
    )
VALUES (
        'Administrador',
        'Administrador de QuillaGPT',
        true
    ),
    (
        'Estudiante',
        'Alumno de la Facultad de Ciencias e Ingenieria',
        true
    );

-- CREATE TABLE `File` (
--   `file_id` integer PRIMARY KEY AUTO_INCREMENT,
--   `user_id` integer,
--   `content` mediumblob,
--   `type` varchar(255),
--   `name` varchar(255),
--   `register_date` date,
--   `active` bool
-- );

CREATE TABLE `File` (
    `file_id` integer PRIMARY KEY AUTO_INCREMENT,
    `content` mediumblob,
    `type` varchar(255),
    `name` varchar(255),
    `created_by` integer,
    `register_date` date,
    `created_at` date DEFAULT(now()),
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `modified_by` integer,
    `active` bool
);

-- CREATE TABLE `CustomInstruction` (
--   `custom_instruction_id` integer PRIMARY KEY AUTO_INCREMENT,
--   `instruction` TEXT,
--   `register_date` date,
--   `user_id` integer,
--   `active` bool
-- );

CREATE TABLE `CustomInstruction` (
    `custom_instruction_id` integer PRIMARY KEY AUTO_INCREMENT,
    `instruction` TEXT,
    `register_date` date,
    `created_by` integer,
    `created_at` date DEFAULT(now()),
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `modified_by` integer,
    `active` bool
);

-- CREATE TABLE `RequestQuery` (
--   `request_query_id` integer PRIMARY KEY AUTO_INCREMENT,
--   `query` varchar(255),
--   `reply` varchar(255),
--   `classification` varchar(255),
--   `register_date` date,
--   `resolved` bool,
--   `user_id` integer,
--   `context` TEXT COMMENT 'holds the context of the message',
--   `active` bool
-- );

CREATE TABLE `RequestQuery` (
    `request_query_id` integer PRIMARY KEY AUTO_INCREMENT,
    `query` varchar(255),
    `reply` varchar(255),
    `classification` varchar(255),
    `register_date` date,
    `resolved` bool,
    `session_id` integer,
    `context` TEXT COMMENT 'holds context of the message',
    `created_at` date DEFAULT(now()),
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` integer,
    `modified_by` integer,
    `active` bool
);

-- ALTER TABLE `Message` ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

-- ALTER TABLE `Session` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

-- ALTER TABLE `File` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

-- ALTER TABLE `User` ADD FOREIGN KEY (`role_id`) REFERENCES `Role` (`role_id`);

-- ALTER TABLE `SessionClassification` ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

-- ALTER TABLE `RequestQuery` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

-- ALTER TABLE `CustomInstruction` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

ALTER TABLE `Message`
ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

ALTER TABLE `Session`
ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

ALTER TABLE `CustomInstruction`
ADD FOREIGN KEY (`modified_by`) REFERENCES `User` (`user_id`);

ALTER TABLE `CustomInstruction`
ADD FOREIGN KEY (`created_by`) REFERENCES `User` (`user_id`);

ALTER TABLE `RequestQuery`
ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

ALTER TABLE `User`
ADD FOREIGN KEY (`role_id`) REFERENCES `Role` (`role_id`);

ALTER TABLE `SessionClassification`
ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

ALTER TABLE `File`
ADD FOREIGN KEY (`modified_by`) REFERENCES `User` (`user_id`);

ALTER TABLE `File`
ADD FOREIGN KEY (`created_by`) REFERENCES `User` (`user_id`);

ALTER TABLE `RequestQuery`
ADD FOREIGN KEY (`modified_by`) REFERENCES `User` (`user_id`);

ALTER TABLE `RequestQuery`
ADD FOREIGN KEY (`created_by`) REFERENCES `User` (`user_id`);

INSERT INTO
    `User` (
        `role_id`,
        `name`,
        `email`,
        `active`
    )
VALUES (
        1,
        'ALEX PAN LI',
        'alex.pan@pucp.edu.pe',
        true
    );

-- INSERT INTO `CustomInstruction` (`instruction`, `active`)
-- VALUES
-- ('Te llamas QuillaGPT y ayudas sobre procesos académico-administrativos de la PUCP. Si encuentras información sobre el proceso académico-administrativo consultado por el usuario, tienes que explicar de manera simple pero detallada el procedimiento o los pasos que tiene que hacer. Lo siguiente que debes hacer es mencionar la fuente de donde has sacado la información. La fuente lo sacas según el link anexado (si es que el link se encuentra añadido a la información) y en los casos particulares que la información extraída fue sacada de un documento entonces debes mencionar el nombre del documento del cual has sacado información. Asimismo, menciona que si la información recogida no tiene relación con la consulta del estudiante, si el estudiante lo desea, puede realizar la derivación de la consulta con el administrador dando clic al pulgar abajo al mensaje.', true);

INSERT INTO
    `CustomInstruction` (
        `instruction`,
        `register_date`,
        `created_by`,
        `active`
    )
VALUES (
        'Rol general:
Eres PandaGPT, un asistente virtual que apoya a los estudiantes de la Pontificia Universidad Católica del Perú (PUCP) con consultas relacionadas exclusivamente a trámites y procedimientos académico-administrativos de la Facultad de Ciencias e Ingeniería (FCI).

Alcance y restricciones:
1. Cobertura limitada: Solo respondes preguntas relacionadas con la Facultad de Ciencias e Ingeniería (FCI), caso contrario, debes responder que no puedes atender la consulta porque está fuera de tu alcance.
2. Falta de información o resultados irrelevantes: Si no tienes información suficiente o los resultados no responden claramente a la pregunta, indica que no puedes atender la consulta porque no tienes conocimiento al respecto.
3. Consultas fuera del ámbito académico-administrativo: Responde con cortesía y redirecciona la conversación hacia temas relacionados con la PUCP.

Si tienes información útil, sigue estas pautas:
1. Claridad y detalles: 
- Menciona el nombre del trámite académico-administrativo.
- Si tienes los pasos del proceso, descríbelos con claridad.
- Si una de las fuentes proviene del Google Sites y el nombre del trámite tiene que ver con esa fuente, le mencionas que es importante mencionarle que FCI recomienda realizar el trámite por medio de los formularios a través de la plataforma Kissflow y le adjuntas el enlace.
2. Fuente:
- Indica de dónde proviene la información.
- Si es de una página web, incluye el enlace.
- Si es de un documento, menciona su nombre.
- Si tienes varios enlaces que realmente están relacionados con la consulta, adjúntalos.
3. Fecha de extracción:
- Informa la fecha en que fue obtenida la información.
4. Naturalidad
- Usa un tono amable y cercano.
- Evita sonar robótico o excesivamente formal.
5. Información adicional (cuando aplique)
- Medio de contacto: ¿Cómo puede el estudiante obtener más información?',
        CURDATE(),
        1,
        true
    );