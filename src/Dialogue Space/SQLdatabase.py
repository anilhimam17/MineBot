import sqlite3

def initialize_database():
    """Create game database and chart"""
    conn = sqlite3.connect("game_state.db")  # Connect the database（if not exist, automatically create）
    cursor = conn.cursor()

    # Create game state chart
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            life INTEGER NOT NULL,
            experience INTEGER NOT NULL,
            inputString TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_game_state(player_name, life, experience, String):
    """Save the player's game status"""
    conn = sqlite3.connect("game_state.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO game_state (player_name, life, experience, inputString) 
        VALUES (?, ?, ?, ?)
    """, (player_name, life, experience, String))

    conn.commit()
    conn.close()
    #print(f"Game status saved: {player_name} | life: {life} | experience: {experience} | input: {String}")


def load_game_state(player_name):
    """Load the game status of the specified player"""
    conn = sqlite3.connect("game_state.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT life, experience, inputString, timestamp FROM game_state
        WHERE player_name = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (player_name,))

    result = cursor.fetchone()
    conn.close()

    if result:
        life, experience, inputString, timestamp = result
        #print(f"Player {player_name} game status: life {life}, experience {experience}, input{inputString}, Time {timestamp}")
        return result
    else:
        print(f"Fail to find {player_name} game status")
        return None

def update_game_state(player_name, new_life, new_experience, String):
    """Update players game status"""
    conn = sqlite3.connect("game_state.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE game_state 
        SET life = ?, experience = ?, inputString = ?, timestamp = CURRENT_TIMESTAMP
        WHERE player_name = ?
    """, (new_life, new_experience, String, player_name))

    conn.commit()
    conn.close()
    #print(f"{player_name} game status has been updated:life {new_life}, experience {new_experience}, input{String}")

def delete_game_state(player_name):
    """Delete a player's save"""
    conn = sqlite3.connect("game_state.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM game_state WHERE player_name = ?", (player_name,))
    
    conn.commit()
    conn.close()
    #print(f"{player_name} save has been deleted")

# Get life of a player
def get_player_life(player_name):
    state = load_game_state(player_name)
    if state != None:
        life, experience, inputString, timestamp = state
        return life
    else:
        print("Fail to get the life")

# Get experience of a player
def get_player_experience(player_name):
    state = load_game_state(player_name)
    if state != None:
        life, experience, inputString, timestamp = state
        return experience
    else:
        print("Fail to get the experience")

# Get input of a player
def get_player_input(player_name):
    state = load_game_state(player_name)
    if state != None:
        life, experience, inputString, timestamp = state
        return inputString
    else:
        print("Fail to get the input")

if __name__ == "__main__": # Test
    initialize_database()
    save_game_state("Alice", 10, 20, "Hello, World")
    save_game_state("Bob", 5, 15, "How to build a house?")
    update_game_state("Alice", 10, 25, "I have made a stove")
    #life_Alice = get_player_life("Alice")
    #print(f"Alice's life: {life_Alice}")
    String_Alice = get_player_input("Alice")
    print(String_Alice)