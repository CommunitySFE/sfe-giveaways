from server import app, session
import json

@app.route("/auth/session")
def create_session_token(self):
    return json.dumps({"token": session.create_session()})

@app.route("/auth/session/{token}")
def get_session_status(self, token):
    return json.dumps({
        "authenticated": session.is_session_authenticated(token),
        "user_id": session.sessions[token] if session.is_session_authenticated(token) else None
    })