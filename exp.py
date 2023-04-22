import datetime
import pytz

import main

con, cur = main.get_connection()
names = [name[0] for name in cur.execute("SELECT name FROM sqlite_master WHERE type='table';")]
print(names)
