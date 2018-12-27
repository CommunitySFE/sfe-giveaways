from disco.bot import Plugin, Config
from disco.api.http import APIException
from flask import request
import json
import random

class BackendPluginConfig(Config):
    
    captcha_site_key = "0"
    master_guild = "0"
    web_permissions_role_id = "0"


@Plugin.with_config(BackendPluginConfig)
class BackendPlugin(Plugin):

    def load(self, ctx):
        self.sessions = dict()
        self.bot.http.register_error_handler(404, self.not_found_response)
        self.ok_response = "200 ok"
        super(BackendPlugin, self).load(ctx)
    
    def not_found_response(self, error):
        return (json.dumps({"error": error.name}), "404 not found", {"Content-Type": "application/json"})
    
    def bad_request_response(self, error_description, error_code="400", error_name="bad request"):
        return (
            json.dumps({"error": error_description}),
            "{code} {name}".format(code=error_code, name=error_name),
            {"Content-Type": "application/json"}
        )

    def get_token(self, user_id):
        base = self.bot.plugins["BasePlugin"]
        return base.web_tokens.find_one({
            "user_id": int(user_id)
        })
    
    def get_auth_status(self, token):
        """
        Returns the user ID of a given token.

        It also returns None if the token is invalid or unauthenticated.
        """
        if token is None:
            return None
        base = self.bot.plugins["BasePlugin"]
        try:
            token = int(token)
        except ValueError:
            return None
        return base.web_tokens.find_one({
            "token": token
        })
    
    @Plugin.route("/api/auth/session", methods=["GET"])
    def session_create(self):
        session_id = random.randint(10**16, 10**17)
        self.sessions[session_id] = None
        return (json.dumps({"session_id": session_id}), self.ok_response, {"Content-Type": "application/json"})

    @Plugin.command("authenticate", "<token:int>", level=100)
    def authenticate_session(self, event, token):
        if self.sessions.get(token) is not None:
            event.msg.reply(":no_entry_sign: invalid token")
            return
        
        self.sessions[token] = event.msg.author.id
        event.msg.reply(":ok_hand: authenticated. press `next` on the dashboard to continue.")
    
    @Plugin.route("/api/auth/session/<session>", methods=["GET"])
    def session_get_status(self, session):
        # Make sure session is an integer, and not some other stupid input.
        try:
            session = int(session)
        except ValueError:
            return self.bad_request_response("session token must be an integer")

        # Determine authentication and return response
        if self.sessions.get(int(session)) is None:
            return (json.dumps({"authenticated": False}), self.ok_response, {"Content-Type": "application/json"})
        
        return (json.dumps({
            "authenticated": True,
            "user_id": self.sessions[int(session)],
            "session_id": session
        }), self.ok_response, {"Content-Type": "application/json"})
    
    @Plugin.route("/api/auth/session/<session>/use", methods=["POST"])
    def session_get_token(self, session):
        # Check to make sure the session can be parsed as an integer
        try:
            session = int(session)
        except ValueError:
            return self.bad_request_response("session id must be an integer")
        
        # Determine whether the token is authenticated
        session_user = self.sessions.get(session)

        if session_user is None:
            return self.bad_request_response("session not authenticated", "401", "unauthorized")
        
        # See if an existing token exists
        existing_token = self.get_token(session_user)
        if existing_token is not None:
            # Delete existing token to prevent malicious use.
            self.bot.plugins["BasePlugin"].web_tokens.delete_one({
                "token": existing_token["token"]
            })
        
        token = random.randint(10**16, 10**17)
        self.bot.plugins["BasePlugin"].web_tokens.insert_one({
            "token": token,
            "user_id": session_user
        })

        del self.sessions[session]
        return (json.dumps({
            "token": token,
            "deleted_previous_token": existing_token is not None
        }), self.ok_response, {"Content-Type": "application/json"})
    
    @Plugin.route("/api/users/me", methods=["GET"])
    def users_me(self):
        # Make sure user is authenticated with a token.
        user_auth = self.get_auth_status(request.headers.get("Authorization"))
        if not user_auth:
            return self.bad_request_response("invalid token", "401", "unauthorized")
        
        if not user_auth.get("user_id"):
            return self.bad_request_response("invalid database token object", "500", "internal server error")
        
        try:
            user = self.bot.client.api.guilds_members_get(self.config.master_guild, user_auth.get("user_id"))
        except APIException:
            return self.bad_request_response("failed to find user.")

        permission_value = 0
        
        if int(self.config.web_permissions_role_id) in user.roles:
            permission_value = 1

        return (
            json.dumps({
                "username": user.user.username,
                "discriminator": user.user.discriminator,
                "permission_value": permission_value
            }),
            self.ok_response,
            {
                "Content-Type": "application/json"
            }
        )
        