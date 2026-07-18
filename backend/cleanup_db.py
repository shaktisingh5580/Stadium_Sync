import sqlite3

try:
    conn = sqlite3.connect('c:/Users/shakt/Downloads/Hack2skill/backend/stadium_sync.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM incidents WHERE ticket_id = 'sim-cv-node'")
    deleted_rows = cursor.rowcount
    conn.commit()
    print(f"Successfully deleted {deleted_rows} test incidents from the database.")
except Exception as e:
    print(f"Error connecting to database or executing query: {e}")
finally:
    if 'conn' in locals():
        conn.close()
