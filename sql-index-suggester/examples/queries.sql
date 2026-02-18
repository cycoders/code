SELECT * FROM users WHERE email = 'foo@bar.com' ORDER BY created_at DESC;
SELECT * FROM orders o JOIN users u ON o.user_id = u.id WHERE o.status = 'shipped' AND o.amount > 100 ORDER BY o.created_at;
SELECT status FROM orders WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY status ORDER BY status;