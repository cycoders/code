def get_user(user_id):
    return cursor.execute("SELECT * FROM users WHERE id=" + str(user_id))