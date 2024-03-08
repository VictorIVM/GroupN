CREATE TABLE `registrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `registration_number` varchar(15) NOT NULL,
  `semester` varchar(10) NOT NULL,
  `year` varchar(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `registration_number` (`registration_number`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(50) NOT NULL,
  password VARCHAR(128) NOT NULL,
  role ENUM('student', 'teacher', 'admin') NOT NULL,
  course VARCHAR(50),
  admin_role ENUM('0', '1') DEFAULT '0',
  student_id VARCHAR(50) NOT NULL,
  picture VARCHAR(255),
  UNIQUE (email),
  UNIQUE (student_id)
);


CREATE TABLE `nominations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `candidate_name` varchar(100) NOT NULL,
  `position` varchar(50) NOT NULL,
  `votes` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `nominations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    starting_time DATETIME NOT NULL,
    ending_time DATETIME NOT NULL
);

CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position VARCHAR (100) NOT NULL,
    profile TEXT NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    student_id VARCHAR(100) NOT NULL
);

CREATE TABLE position_time (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position_id INT,
    starting_time DATETIME,
    ending_time DATETIME,
    FOREIGN KEY (position_id) REFERENCES positions(id)
);