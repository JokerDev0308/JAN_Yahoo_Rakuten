import json
from pathlib import Path
import hashlib
from typing import Optional, Dict

class SessionManager:
    def __init__(self):
        self.users_file = Path("data/users.json")
        self._init_files()

    def _init_files(self):
        if not self.users_file.exists():
            default_users = {
                "admin": {
                    "password": hashlib.sha256("password123".encode()).hexdigest(),
                    "role": "admin"
                }
            }
            self.users_file.parent.mkdir(exist_ok=True)
            self.users_file.write_text(json.dumps(default_users))

    def validate_user(self, username: str, password: str) -> bool:
        users = json.loads(self.users_file.read_text())
        if username in users:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            return users[username]["password"] == hashed_password
        return False