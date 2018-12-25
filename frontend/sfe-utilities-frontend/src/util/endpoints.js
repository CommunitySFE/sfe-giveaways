
const Endpoints = {
    AUTH_GET_SESSION: "/auth/session",
    AUTH_GET_SESSION_STATUS: function(token) {
        return "/auth/session/" + encodeURI(token)
    }
};

export default Endpoints;