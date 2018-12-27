import React, { Component } from 'react';
import API from './../util/api'
import { Endpoints } from './../util/endpoints'

class DashboardBodyComponent extends Component {
    render() {
        return (
            <Dashboard />
        );
    }
}

class Dashboard extends Component {
    constructor(props) {
        super(props)
        this.state = {
            username: "loading",
            discriminator: "0000",
            permissionLevel: 0,
            loaded: false
        }
        if (!window.localStorage["token"]) {
            window.location = "/auth/login"
        }
    }

    render() {
        if (!this.state.loaded) {
            return (
                <div>
                    <h1>Dashboard</h1>
                    <br />
                    <p>Loading...</p>
                </div>
            )
        }
        return (
            <div>
                <h1>Dashboard</h1>
                <br />
                <p>Hello, {this.state.username}#{this.state.discriminator}.</p>
                <DashboardModuleCard 
                    moduleUrl="/auth/logout"
                    moduleName="Logout"
                    moduleDescription="Open this module to logout of your account."
                    permissionsRequired={0}
                    permissionLevel={this.state.permissionLevel}
                />
            </div>
        )
    }

    componentDidMount() {
        if (this.state.loaded)
            return;
        
        API.get(Endpoints.USERS_ME, {
            "Authorization": window.localStorage.getItem("token")
        }).then(response => {
            if (!response.ok) {
                // TODO error handler
                switch (response.status) {
                    case 401:
                        window.localStorage.removeItem("token")
                        window.location = "/auth/login"
                        break
                    default:
                        return
                }
                return
            }
            response.json().then(jsonResponse => {
                this.setState({
                    username: jsonResponse["username"],
                    discriminator: jsonResponse["discriminator"],
                    permissionLevel: jsonResponse["permission_value"],
                    loaded: true
                })
            })
        })
    }
}

class DashboardModuleCard extends Component {
    constructor(props) {
        super(props)
        if (!this.props.moduleUrl) {
            console.error("module url cannot be null for a DashboardModuleCard")
            this.state = {
                name: "ERROR",
                description: "An error occurred while loading the module.",
                url: "/dashboard/error",
                visible: false
            }
            return
        }
        console.log(JSON.stringify(props))
        this.state = {
            name: props.moduleName == null ? "Unknown module name" : props.moduleName,
            description: props.moduleDescription,
            url: props.moduleUrl,
            visible: props.permissionLevel >= props.permissionsRequired
        }
    }

    render() {
        // TODO clean this up lol
        if (!this.state.visible) {
            return (
                <div>
                </div>
            )
        }
        return (
            <div className="card mx-3 my-3" style={{width: "18rem"}}>
                <div className="card-body">
                    <h5 className="card-title">{this.state.name}</h5>
                    <p className="card-text">{this.state.description}</p>
                    <a href={this.state.url} className="card-link">Open</a>
                </div>
            </div>
        )
    }
}

export default DashboardBodyComponent;