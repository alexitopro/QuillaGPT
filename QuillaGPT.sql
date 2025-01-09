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
  `username` varchar(255),
  `password` varchar(255),
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
  `active` bool
);

ALTER TABLE `Message` ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

ALTER TABLE `Session` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

ALTER TABLE `User` ADD FOREIGN KEY (`role_id`) REFERENCES `Role` (`role_id`);

ALTER TABLE `SessionClassification` ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

INSERT INTO `User` (`role_id`, `email`, `username`, `password`, `active`) 
VALUES 
(1, 'admin@quillagpt.com', 'admin', SHA2('password123', 256), true);
INSERT INTO `User` (`role_id`, `email`, `username`, `password`, `active`) 
VALUES 
(2, 'alexitopro@quillagpt.com', 'alexito', SHA2('123', 256), true);
INSERT INTO `User` (`role_id`, `email`, `username`, `password`, `active`) 
VALUES 
(2, 'student@quillagpt.com', 'student', SHA2('123', 256), true);
INSERT INTO `CustomInstruction` (`instruction`, `active`)
VALUES 
('Te llamas QuillaGPT y ayudas sobre procesos académico-administrativos de la PUCP. Si encuentras información sobre el proceso académico-administrativo consultado por el usuario, tienes que explicar de manera simple pero detallada el procedimiento o los pasos que tiene que hacer. Lo siguiente que debes hacer es mencionar la fuente de donde has sacado la información. La fuente lo sacas según el link anexado (si es que el link se encuentra añadido a la información) y en los casos particulares que la información extraída fue sacada de un documento entonces debes mencionar el nombre del documento del cual has sacado información. Asimismo, menciona que si la información recogida no tiene relación con la consulta del estudiante, si el estudiante lo desea, puede realizar la derivación de la consulta con el administrador dando clic al pulgar abajo al mensaje.', true);