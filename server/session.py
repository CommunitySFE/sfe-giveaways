import random


class SessionManager:

    def __init__(self):
        self.sessions = dict()
    
    def create_session(self):
        session_id = random.randint(10**16, 10**17)
        if self.sessions.get(session_id) is not None:
            self.create_session()
        self.sessions[session_id] = None
        return session_id
    
    def authenticate_session(self, session_id, user_id):
        if self.sessions.get(session_id) is None:
            return False
        
        self.sessions[session_id] = user_id
        return True
    
    def is_session_authenticated(self, session_id):
        return not self.sessions.get(session_id) is None