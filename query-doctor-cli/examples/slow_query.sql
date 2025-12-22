SELECT * FROM users, orders  -- cartesian join!
WHERE users.id = orders.user_id
  AND orders.amount > 100.00;  -- ok index, but SELECT * + no LIMIT