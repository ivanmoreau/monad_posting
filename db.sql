CREATE DATABASE IF NOT EXISTS `SOCIAL_db`;
USE `SOCIAL_db`;

DROP TABLE IF EXISTS `POST`;
DROP TABLE IF EXISTS `USER_LOGIN`;
DROP TABLE IF EXISTS `FOLLOWER`;
DROP TABLE IF EXISTS `USER_PAGE`;
DROP TABLE IF EXISTS `USER`;
DROP TABLE IF EXISTS `BLOCKED_USER`;

CREATE TABLE IF NOT EXISTS `USER_LOGIN` (
    user_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_mail           VARCHAR (400) NOT NULL,
    password_hash       VARCHAR (255) NOT NULL
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS `USER` (
    user_id             INT NOT NULL PRIMARY KEY,
    user_username       VARCHAR (100) NOT NULL,
    user_allowed        BOOLEAN NOT NULL,
    user_name           VARCHAR (255),
    user_description    VARCHAR (450),
    FOREIGN KEY (user_id) REFERENCES USER_LOGIN(user_id)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS `USER_PAGE` (
    user_id             INT NOT NULL PRIMARY KEY,
    custom_css          VARCHAR (1024) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USER(user_id)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS `POST` (
    post_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id             INT NOT NULL,
    post_text           VARCHAR (400) NOT NULL,
    post_is_repost      BOOLEAN NOT NULL,
    post_father_id      INT,
    post_date           DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USER(user_id),
    FOREIGN KEY (post_father_id) REFERENCES POST(post_id)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS `FOLLOWER` (
    user_id_source      INT NOT NULL,
    user_id_target      INT NOT NULL,
    FOREIGN KEY (user_id_source) REFERENCES USER(user_id),
    FOREIGN KEY (user_id_target) REFERENCES USER(user_id)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS `BLOCKED_USER` (
    user_id_source      INT NOT NULL,
    user_id_target      INT NOT NULL,
    FOREIGN KEY (user_id_source) REFERENCES USER(user_id),
    FOREIGN KEY (user_id_target) REFERENCES USER(user_id)
) ENGINE=INNODB;
