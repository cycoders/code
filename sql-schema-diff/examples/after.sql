CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) NOT NULL UNIQUE,
  age INTEGER
);

CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_age ON users (age);

CREATE TABLE new_table (
  id INTEGER PRIMARY KEY
);
