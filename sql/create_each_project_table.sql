CREATE TABLE project_name (
    `image_id` int(11) NOT NULL AUTO_INCREMENT,
    `file_name` varchar(255) NOT NULL,
    `google_drive_file_id` varchar(255) NOT NULL,
    `create_date` datetime NOT NULL,
    `image_type` varchar(20) NOT NULL,
    `project_id` int(11) NOT NULL,
    PRIMARY KEY (`image_id`),
    KEY `project_id` (`project_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;