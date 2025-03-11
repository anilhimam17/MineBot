from sqlite3 import DatabaseError
from minecraft_assistant.dialogue_space.game_datastore import GameStateDataStore
from minecraft_assistant.dialogue_space.message_datastore import MessageDataStore


def test_game_state_datastore_works() -> bool | None:

    # Create Gamestate Datastore
    game_state_db = GameStateDataStore("./db/game_state_db")
    if game_state_db:
        assert True
    else:
        raise DatabaseError("The database was not created.")


def test_message_datastore_works() -> bool | None:

    # Create Message Datastore
    message_store = MessageDataStore()
    if message_store.message_store == []:
        assert True
    else:
        raise NotImplementedError("Could not find the resource.")
