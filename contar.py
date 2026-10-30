import sqlite3
from contextlib import closing

with closing(sqlite3.connect('solicitudes.db')) as con:
    print(con.execute('SELECT COUNT(*) FROM solicitudes').fetchone()[0])