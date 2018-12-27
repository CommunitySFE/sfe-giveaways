import React, { Component } from 'react';


class LogoutComponent extends Component {
    render() {
        return (
            <div>
                <h1>Logout</h1>
                <br />
                <p>Are you sure you want to logout?</p>
                <button className="btn btn-primary mx-1" onClick={this.logout}>Yes, log me out.</button>
                <button className="btn btn-danger my-1" onClick={this.gotoDashboard}>No, don't log me out.</button>
            </div>
        )
    }

    gotoDashboard() {
        window.location = "/dashboard"
    }

    logout() {
        window.localStorage.removeItem("token")
        window.location = "/"
    }
}

export default LogoutComponent;