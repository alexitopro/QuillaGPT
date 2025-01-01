DROP TABLE IF EXISTS `Message`;
DROP TABLE IF EXISTS `Session`;
DROP TABLE IF EXISTS `CustomInstruction`;
DROP TABLE IF EXISTS `File`;
DROP TABLE IF EXISTS `RequestQuery`;
DROP TABLE IF EXISTS `User`;
DROP TABLE IF EXISTS `Role`;

CREATE TABLE `Session` (
  `session_id` integer PRIMARY KEY AUTO_INCREMENT,
  `start_session` timestamp DEFAULT (now()),
  `end_session` timestamp,
  `user_id` integer,
  `title` varchar(255),
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
  `content` varchar(255),
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
  `instruction` varchar(511),
  `active` bool
);

CREATE TABLE `RequestQuery` (
  `request_query_id` integer PRIMARY KEY AUTO_INCREMENT,
  `query` varchar(255),
  `reply` varchar(255),
  `user_resolved_id` integer,
  `register_date` date,
  `resolved` bool,
  `active` bool
);

ALTER TABLE `Message` ADD FOREIGN KEY (`session_id`) REFERENCES `Session` (`session_id`);

ALTER TABLE `Session` ADD FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`);

ALTER TABLE `User` ADD FOREIGN KEY (`role_id`) REFERENCES `Role` (`role_id`);

ALTER TABLE `RequestQuery` ADD FOREIGN KEY (`user_resolved_id`) REFERENCES `User` (`user_id`);

INSERT INTO `User` (`role_id`, `email`, `username`, `password`, `active`) 
VALUES 
(1, 'admin@quillagpt.com', 'admin', SHA2('password123', 256), true);
INSERT INTO `User` (`role_id`, `email`, `username`, `password`, `active`) 
VALUES 
(2, 'alexitopro@quillagpt.com', 'alexito', SHA2('123', 256), true);
INSERT INTO `User` (`role_id`, `email`, `username`, `password`, `active`) 
VALUES 
(2, 'student@quillagpt.com', 'student', SHA2('123', 256), true);