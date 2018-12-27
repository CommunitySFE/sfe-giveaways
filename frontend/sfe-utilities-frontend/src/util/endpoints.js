
module.exports = {
    Endpoints: {
        AUTH_GET_SESSION: "/api/auth/session",
        AUTH_GET_SESSION_STATUS: function(token) {
            return "/api/auth/session/" + encodeURI(token)
        },
        AUTH_USE_SESSION: function(token) {
            return "/api/auth/session/" + encodeURI(token) + "/use"
        },
        USERS_ME: "/api/users/me"
    },
    APIConstants: {
        // API_PREFIX is now deprecated.
        API_PREFIX: ""
    }
};