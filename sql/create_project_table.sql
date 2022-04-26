CREATE TABLE `project` (
    `project_id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `google_drive_folder_id` varchar(100) NOT NULL,
    `discription` text,
    PRIMARY KEY (`project_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;