# Examples

```bash
poetry run sql-index-suggester schema.sql queries.sql
```

Expected: Suggestions for `orders.user_id,amount`, `orders.created_at`, etc.

Try `--dialect mysql` or `--output json > out.json`.