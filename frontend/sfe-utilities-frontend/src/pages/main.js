import React, { Component } from 'react';

class MainComponent extends Component {

    constructor(props) {
        super(props)
        if (window.localStorage.getItem("token")) {
            window.location = "/dashboard"
        }
    }

    render() {
        return (
            <div>
                <h1>Server Dashboard</h1>
                <br />
                <h3>Actions</h3>
                <div className="row">
                    <div className="col-sm-2">
                        <div className="card" style={{width: "18rem"}}>
                            <div className="card-body">
                                <h5 className="card-title">Authenticate</h5>
                                <p className="card-text">Login to access the dashboard.</p>
                                <button className="btn btn-primary" onClick={this.authenticate}>Login</button>
                            </div>
                        </div>
                    </div>
                    <div className="col-sm-2">
                        <div className="card" style={{width: "18rem"}}>
                            <div className="card-body">
                                <h5 className="card-title">Join</h5>
                                <p className="card-text">Join the server</p>
                                <button className="btn btn-primary" onClick={this.joinServer}>Join</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    joinServer() {
        window.location.href = "https://discord.gg/sfe"
    }

    authenticate() {
        window.location.pathname = "/auth/login"
    }
}

export default MainComponent;