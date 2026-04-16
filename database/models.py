from database.db import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO users (username, password)
    SELECT 'admin', 'admin123'
    WHERE NOT EXISTS (
        SELECT 1 FROM users WHERE username='admin'
    )
    """)

    conn.commit()
    conn.close()