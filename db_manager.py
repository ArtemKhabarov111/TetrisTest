import sqlite3

# Define the database file name
DB_FILE = 'tetris_records.db'


def get_connection():
    return sqlite3.connect(DB_FILE)


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            lines INTEGER NOT NULL,
            level INTEGER NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def insert_dummy_data():
    dummy_records = [
        ("PlayerOne", 500, 40, 5),
        ("TetrisMaster", 1000, 65, 8),
        ("BlockDropper", 1500, 35, 4),
        ("SpeedyG", 2000, 50, 6),
        ("ZShapeHero", 2500, 55, 7),
        ("GreenHouse", 1000, 10, 2)
    ]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO leaderboard (username, score, lines, level)
        VALUES (?, ?, ?, ?);
    """, dummy_records)
    conn.commit()
    conn.close()
    print("Dummy data inserted into leaderboard.")


if __name__ == "__main__":
    initialize_db()
    insert_dummy_data()
    print("Database initialized and leaderboard table populated with dummy data.")
