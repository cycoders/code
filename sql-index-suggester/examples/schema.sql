CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR UNIQUE,
  created_at TIMESTAMP
);

CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  status VARCHAR,
  amount DECIMAL,
  created_at TIMESTAMP
);

CREATE INDEX CONCURRENTLY idx_orders_status ON orders(status);