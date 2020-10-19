CREATE TABLE users (id INTEGER NOT NULL AUTO_INCREMENT, login VARCHAR (20) NOT NULL, username VARCHAR (80) NOT NULL, password_hash VARCHAR (200) NOT NULL, PRIMARY KEY (id), UNIQUE (login)) DEFAULT CHARSET=utf8mb4;
CREATE TABLE note (id INTEGER NOT NULL AUTO_INCREMENT, user_id INTEGER, title VARCHAR (100) NOT NULL, text TEXT, creationDate DATETIME, dueDate DATETIME, isDone BOOLEAN, PRIMARY KEY (id), FOREIGN KEY (user_id) REFERENCES users (id), CHECK (isDone IN (0, 1))) DEFAULT CHARSET=utf8mb4;
