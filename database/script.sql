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

CREATE TABLE IF NOT EXISTS votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position_id INT NOT NULL,
    candidate_id INT NOT NULL,
    voted_by VARCHAR(255) NOT NULL,
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    FOREIGN KEY (voted_by) REFERENCES users(student_id)
);

CREATE TABLE ballot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position_id INT,
    candidate_id INT,
    voter_id INT,
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_position FOREIGN KEY (position_id) REFERENCES positions(id),
    CONSTRAINT fk_candidate FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    CONSTRAINT fk_voter FOREIGN KEY (voter_id) REFERENCES users(id)
);