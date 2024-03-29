CREATE TABLE IF NOT EXISTS table_name_patient (
    `patient_id` int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `google_drive_parent_id` varchar(255),
    `group` varchar(255),
    `project_id` int(11) NOT NULL,
    `google_drive_parent_name` varchar(30) NOT NULL,
    FOREIGN KEY (`project_id`) REFERENCES project(`project_id`) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS table_name_cell (
    `cell_id` int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `cell_type` varchar(20) NOT NULL,
    `cell_number` int NOT NULL,
    `patient_id` int NOT NULL,
    FOREIGN KEY (`patient_id`) REFERENCES table_name_patient(`patient_id`) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS table_name_image (
    `image_id` int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `file_name` varchar(255) NOT NULL,
    `google_drive_file_id` varchar(255),
    `create_date` datetime NOT NULL,
    `image_type` varchar(20) NOT NULL,
    `patient_id` int(10) NOT NULL,
    `cell_id` int(10) NOT NULL,
    FOREIGN KEY(`patient_id`) REFERENCES table_name_patient(`patient_id`) ON UPDATE CASCADE,
    FOREIGN KEY (`cell_id`) REFERENCES table_name_cell(`cell_id`) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS table_name_image_quality (
    `image_id` int(10) PRIMARY KEY,
    `quality` int
);

CREATE TABLE IF NOT EXISTS table_name_image_center (
    `image_id` int(10) PRIMARY KEY,
    `x` int(5) NOT NULL,
    `y` int(5) NOT NULL,
    `z` int(5) NOT NULL
);