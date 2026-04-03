import datetime
import time

# These will trigger issues
dt1 = datetime.now()  # error: naive now()
dt2 = datetime.utcnow()  # error: naive utcnow()
dt3 = datetime.fromtimestamp(time.time())  # error: naive fromtimestamp
dt4 = datetime.strptime("2023-01-01", "%Y-%m-%d")  # warning: strptime no tz
dt5 = datetime(2023, 1, 1, 12, 0)  # warning: constructor no tzinfo
