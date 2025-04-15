import sqlite3

# Name of DB
DB_FILE = 'tetris_records.db'


def get_connection():
    return sqlite3.connect(DB_FILE)


def initialize_db():
    # Create leaderboard table if it doesn't exist
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            level INTEGER NOT NULL,
            lines INTEGER NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def get_high_score():
    # Return the highest score currently in the leaderboard or 0 if the table is empty
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(score) FROM leaderboard;")
    result = cursor.fetchone()[0]
    conn.close()
    return result or 0


def insert_score(username, score, lines, level):
    # Insert a new record into the leaderboard
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leaderboard (username, score, level, lines) VALUES (?, ?, ?, ?);",
        (username, score, lines, level)
    )
    conn.commit()
    conn.close()


def insert_test_data():
    # Test records that will be displayed in the leaderboard
    test_records = [
        ("Sponge Bob", 7000, 4, 31),
        ("Gary", 5000, 3, 21),
        ("Darwin", 4800, 3, 24),
        ("Patrick", 3500, 2, 17),
        ("Nicole", 2100, 2, 12),
        ("Richard", 1700, 2, 12),
        ("Sandy", 1500, 2, 11),
        ("Squidward", 500, 1, 5),
        ("Plankton", 700, 1, 7),
        ("Newbie", 100, 1, 1)
    ]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO leaderboard (username, score, level, lines)
        VALUES (?, ?, ?, ?);
    """, test_records)
    conn.commit()
    conn.close()
    print("Test data inserted into leaderboard.")


# Run this file to initialize leaderboard with test data
if __name__ == "__main__":
    initialize_db()
    insert_test_data()
    print("Database initialized and leaderboard table populated with test data.")
