import sqlite3

conn = sqlite3.connect('pantauresi.db', check_same_thread=False)
cursor = conn.cursor()

create_waybill_table = '''CREATE TABLE IF NOT EXISTS waybill (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chat_id TEXT NOT NULL,
                            waybill TEXT NOT NULL,
                            courier integer NOT NULL,
                            manifest TEXT NOT NULL,
                            status TEXT NOT NULL);'''

cursor.execute(create_waybill_table)
conn.commit()