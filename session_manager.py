import json
from pathlib import Path
import hashlib
from typing import Optional, Dict

class SessionManager:
    def __init__(self):
        self.sessions_file = Path("data/sessions.json")
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

        if not self.sessions_file.exists():
            self.sessions_file.parent.mkdir(exist_ok=True)
            self.sessions_file.write_text("{}")

    def create_session(self, username: str) -> str:
        session_id = hashlib.sha256(f"{username}".encode()).hexdigest()
        sessions = json.loads(self.sessions_file.read_text())
        sessions[session_id] = {"username": username}
        self.sessions_file.write_text(json.dumps(sessions))
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        sessions = json.loads(self.sessions_file.read_text())
        return sessions.get(session_id)

    def validate_user(self, username: str, password: str) -> bool:
        users = json.loads(self.users_file.read_text())
        if username in users:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            return users[username]["password"] == hashed_password
        return False