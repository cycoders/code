CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255),
  created_at TIMESTAMP
);

CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  amount DECIMAL(10,2)
);

CREATE INDEX idx_orders_user_id ON orders (user_id);