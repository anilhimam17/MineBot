from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class MessageDataStore:
    # Message Store
    message_store: list[str] = field(default_factory=list)

    # Class Variables
    n_past_messages: ClassVar[int] = 5

    def add_message(self, message: str) -> None:
        self.message_store.append(message)

    def load_past_messages(self) -> list[str]:
        start_idx = len(self.message_store) - self.n_past_messages
        return self.message_store[start_idx:]
