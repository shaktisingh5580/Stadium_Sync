import sqlite3
conn = sqlite3.connect('stadium_sync.db')
cursor = conn.cursor()
cursor.execute("UPDATE gates SET svg_x=400.0, svg_y=30.0 WHERE name='Gate North'")
cursor.execute("UPDATE gates SET svg_x=400.0, svg_y=770.0 WHERE name='Gate South'")
cursor.execute("UPDATE gates SET svg_x=770.0, svg_y=400.0 WHERE name='Gate East'")
cursor.execute("UPDATE gates SET svg_x=30.0, svg_y=400.0 WHERE name='Gate West'")
conn.commit()
print("DB Gates Updated!")
