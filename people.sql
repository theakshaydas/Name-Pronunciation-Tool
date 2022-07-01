CREATE TABLE IF NOT EXISTS people (
	id serial PRIMARY KEY,
	name VARCHAR ( 20 ) NOT NULL,
	password VARCHAR ( 20 ) NOT NULL,
	email_id VARCHAR ( 80 ) UNIQUE NOT NULL,
	audio VARCHAR (15) NULL,
    preferred_name VARCHAR (20) NULL 
);
INSERT INTO people (name, password, email_id) VALUES ('admin', 'H@ckathon22', 'admin@gmail.com');
INSERT INTO people (name, password, email_id) VALUES ('Akshay Kumar', 'Akshay@22', 'akshay.kumar@gmail.com');
INSERT INTO people (name, password, email_id) VALUES ('Akshay Kumar Das', 'Akshay@22', 'akshay.k.das@gmail.com');
INSERT INTO people (name, password, email_id) VALUES ('Akshaya Das', 'Akshay@22', 'akshay.das@gmail.com');
INSERT INTO people (name, password, email_id) VALUES ('Karthik Peddi', 'Karthik@22', 'karthik.peddi@gmail.com');
INSERT INTO people (name, password, email_id) VALUES ('Shreyas V', 'Shreyas@22', 'shreyas.v@gmail.com');
INSERT INTO people (name, password, email_id) VALUES ('Vijay Lather', 'Vijay@22', 'Vijay.lather@gmail.com');
INSERT INTO people (name, password, email_id) VALUES ('Chaitanya Rai', 'Chaitanya@22', 'chaitanya.rai@gmail.com');
