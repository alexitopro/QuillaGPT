CREATE TABLE `session` (
  `session_id` integer PRIMARY KEY AUTO_INCREMENT,
  `start_session` timestamp DEFAULT (now()),
  `end_session` timestamp,
  `user_id` integer,
  `title` varchar(255),
  `active` bool
);

CREATE TABLE `message` (
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

CREATE TABLE `user` (
  `user_id` integer PRIMARY KEY AUTO_INCREMENT,
  `role_id` integer,
  `email` varchar(255),
  `username` varchar(255),
  `password` varchar(255),
  `active` bool
);

CREATE TABLE `role` (
  `role_id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `description` varchar(255),
  `active` bool
);

CREATE TABLE `file` (
  `file_id` integer PRIMARY KEY AUTO_INCREMENT,
  `content` blob,
  `name` varchar(255),
  `register_date` date,
  `active` bool
);

CREATE TABLE `custom_instruction` (
  `custom_instruction_id` integer PRIMARY KEY,
  `instruction` varchar(255),
  `active` bool
);

CREATE TABLE `request_query` (
  `request_query_id` integer PRIMARY KEY AUTO_INCREMENT,
  `query` varchar(255),
  `reply` varchar(255),
  `user_resolved_id` integer,
  `register_date` date,
  `resolved` bool,
  `active` bool
);

ALTER TABLE `message` ADD FOREIGN KEY (`session_id`) REFERENCES `session` (`session_id`);

ALTER TABLE `session` ADD FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);

ALTER TABLE `user` ADD FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`);

ALTER TABLE `request_query` ADD FOREIGN KEY (`user_resolved_id`) REFERENCES `user` (`user_id`);
