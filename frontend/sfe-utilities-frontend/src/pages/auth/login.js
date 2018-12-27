import React, { Component } from 'react';
import { Endpoints } from './../../util/endpoints';
import API from "./../../util/api";


class AuthenticationLoginComponent extends Component {
    
    render() {
        return (
            <LoginComponent />
        )
    }
}

class LoginComponent extends Component {

    constructor(props) {
        super(props)
        this.state = {
            code: "loading",
            error: ""
        }
        this.checkAuth = this.checkAuth.bind(this)
    }

    render() {
        return (
            <div>
                <h1>Authenticate</h1>
                <br />
                <p color="red">{this.state.error}</p>
                <p>You can authenticate yourself using the following instructions:</p>
                <ol>
                    <li>Go into the commands channel on Discord.</li>
                    <li>Type in <b>.authenticate</b> followed by the code below.</li>
                    <li>Then, press <b>Next</b>.</li>
                </ol>
                <p id="login-code-box">Your code is: <b>{this.state.code}</b></p>
                <button className="btn btn-success" id="login-continue" onClick={this.checkAuth}>Next</button>
            </div>
        );
    }

    componentDidMount() {
        this.updateCode();
    }

    updateCode() {
        API.get(Endpoints.AUTH_GET_SESSION).then(response => {
            if (!response.ok) {
                console.error(response.status + " " + response.statusText)
                return;
            }
            response.json().then(jsonData => {
                var code = jsonData["session_id"]
                this.setState({code: code})
            })
        }).catch(reject => {
            console.error(JSON.stringify(reject))
        })
    }

    checkAuth() {
        API.get(Endpoints.AUTH_GET_SESSION_STATUS(this.state.code)).then(response => {
            if (!response.ok) {
                console.error(response.status + " " + response.statusText);
                return
            }
            response.json().then(jsonResponse => {
                if (!jsonResponse["authenticated"]) {
                    this.setState({ error: "You shall not pass. (try authenticating again lol)" })
                    return
                }

                window.localStorage.setItem("session", this.state.code)
                window.location.pathname = "/auth/confirm"
            })
        })
    }
}

export default AuthenticationLoginComponent;