import MainComponent from './pages/main';
import PageNotFoundComponent from './pages/404';
import LoginComponent from './pages/auth/login';
import AuthenticationConfirmationComponent from './pages/auth/confirm.js'
import DashboardBodyComponent from './pages/dashboard';
import LogoutComponent from './pages/auth/logout';

const Routes = {
    MAIN: {
        location: "/",
        component: new MainComponent()
    },
    AUTH_LOGIN: {
        location: "/auth/login",
        component: new LoginComponent()
    },
    AUTH_CONFIRM: {
        location: "/auth/confirm",
        component: new AuthenticationConfirmationComponent()
    },
    PAGE_NOT_FOUND: {
        location: null,
        component: new PageNotFoundComponent()
    },
    DASHBOARD: {
        location: "/dashboard",
        component: new DashboardBodyComponent()
    },
    LOGOUT: {
        location: "/auth/logout",
        component: new LogoutComponent()
    }
}

export default Routes;