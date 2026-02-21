-- Postgres demo: ILIKE, INTERVAL, NOW()
SELECT name FROM users
WHERE name ILIKE '%test%'
  AND created_at >= NOW() - INTERVAL '7 days'
LIMIT 10 OFFSET 5;

-- WITH CTE
WITH active_users AS (
  SELECT * FROM users WHERE active = true
)
SELECT COUNT(*) FROM active_users;