import sqlite3

def add_conversation_id_column(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE chat_messages ADD COLUMN conversation_id TEXT NOT NULL DEFAULT 'default_conversation';")
        conn.commit()
        print("Column 'conversation_id' added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'conversation_id' already exists.")
        else:
            print(f"Error adding column: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    db_path = "./istqb_assistant.db"
    add_conversation_id_column(db_path)
