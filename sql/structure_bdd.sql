CREATE DATABASE IF NOT EXISTS `meteo`;
USE `meteo`;

CREATE TABLE IF NOT EXISTS `bme` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `date` DATE NOT NULL,
    `temperature` FLOAT NOT NULL,
    `humidity` FLOAT NOT NULL,
    `pressure` FLOAT NOT NULL,
    `luminosity` FLOAT NOT NULL,
    `rain` FLOAT NOT NULL,
    `wind` FLOAT NOT NULL,
    `wind_direction` FLOAT NOT NULL,
    `wind_speed` FLOAT NOT NULL,
    `air_quality` FLOAT NOT NULL,
    `dust` FLOAT NOT NULL,
    `uv` FLOAT NOT NULL,
    PRIMARY KEY (`id`));