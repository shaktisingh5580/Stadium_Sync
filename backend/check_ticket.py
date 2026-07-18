import sqlite3

def main():
    conn = sqlite3.connect('stadium_sync.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, is_active, is_scanned FROM tickets WHERE id='ticket-001'")
    row = cursor.fetchone()
    print("Ticket 001:", row)
    
    # Just to see what tickets exist
    cursor.execute("SELECT count(*) FROM tickets")
    print("Total tickets:", cursor.fetchone()[0])
    
if __name__ == '__main__':
    main()
