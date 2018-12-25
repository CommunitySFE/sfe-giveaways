import React, { Component } from 'react';
import Endpoints from './../../util/endpoints';

class LoginComponent extends Component {
    render() {

        return (
            <div>
                <h1>Authenticate</h1>
                <br />
                <p>You can authenticate yourself using the following instructions:</p>
                <ol>
                    <li>Go into the commands channel on Discord.</li>
                    <li>Type in <b>.authenticate</b> followed by the code below.</li>
                    <li>Then, press <b>Next</b>.</li>
                </ol>
                <p>Your code is: <b>{this.getCode()}</b></p>
                <button className="btn btn-success">Next</button>
            </div>
        );
    }

    getCode() {
        // TODO implement codes
        return "Codes not implemented yet"
    }
}

export default LoginComponent;