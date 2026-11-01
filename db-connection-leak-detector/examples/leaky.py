def get_user(db, user_id):
    conn = db.connect()
    return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
# leak: connection never returned to pool