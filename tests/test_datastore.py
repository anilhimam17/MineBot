from sqlite3 import DatabaseError
from src.dialogue_space.SQLdatabase import DataStore


def test_datastore_creation_works() -> bool | None:
    # Create Datastore
    game_state_db = DataStore("./db/game_state_db")
    if game_state_db:
        assert True
    else:
        raise DatabaseError("The database was not created.")
