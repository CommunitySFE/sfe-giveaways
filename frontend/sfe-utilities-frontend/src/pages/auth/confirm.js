import React, { Component } from 'react';
import { Endpoints } from './../../util/endpoints';
import API from "./../../util/api";


class AuthenticationConfirmationComponent extends Component {
    
    render() {
        return (
            <ConfirmationComponent />
        )
    }
}

class ConfirmationComponent extends Component {

    constructor(props) {
        super(props)
        this.state = {
            "session": window.localStorage.getItem("session")
        }
        if (!this.state.session) {
            window.location = "/auth/login"
        }
        this.accept = this.accept.bind(this)
    }

    render() {
        return (
            <div>
                <h1>Confirm authentication</h1>
                <br />
                <p>The authentication process is complete. Please confirm that you are authorized to use this panel, and that you are not using it maliciously.</p>
                <button className="btn btn-primary" onClick={this.accept}>Confirm</button>
            </div>
        )
    }

    accept() {
        // fix my drunk code or whatever
        API.post(Endpoints.AUTH_USE_SESSION(this.state.session)).then(response => {
            if (!response.ok) {
                alert("an error occurred - please try authenticating again.")
                window.location = "/auth/login"
                return
            }
            response.json().then(jsonResponse => {
                if (!jsonResponse["token"]) {
                    alert("whoops, an error occurred. let's try this again.")
                    console.warn("invalid repsonse from server: " + JSON.stringify(jsonResponse))
                    window.location = "/auth/login"
                }
                if (jsonResponse["token"] == null) {
                    return
                }
                window.localStorage.setItem("token", jsonResponse["token"])
                window.localStorage.removeItem("session")
                window.location = "/dashboard"
            })
        })
    }
}

export default AuthenticationConfirmationComponent;