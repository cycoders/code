from lease_guard import LeaseClient

client = LeaseClient()
lease = client.acquire("db/write-lock", ttl=60)
print("holding", lease.token)
# critical section
lease.release()