# Example with N+1
for user in session.query(User):
    print(user.orders)  # triggers N+1