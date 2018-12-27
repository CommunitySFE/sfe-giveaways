
module.exports = {
    get: function(url, headers={}) {
        return fetch(url, {
            method: "GET",
            headers: headers
        })
    },
    post: function(url, data, headers={}) {
        headers["Content-Type"] = "application/json"
        return fetch(url, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(data)
        })
    }
    // TODO: patch, put, and delete functions
}