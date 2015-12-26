import os
basepath = os.path.dirname(os.path.realpath(__file__))

database = ":memory:"
# database = os.path.join(basepath, "db.sqlite3")

host = "localhost"
port = 8080

production = False

queue_polling_interval = 30
