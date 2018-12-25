import MainComponent from './pages/main';
import PageNotFoundComponent from './pages/404';
import LoginComponent from './pages/auth/login';

const Routes = {
    MAIN: {
        location: "/",
        component: new MainComponent()
    },
    AUTH_LOGIN: {
        location: "/auth/login",
        component: new LoginComponent()
    },
    PAGE_NOT_FOUND: {
        location: null,
        component: new PageNotFoundComponent()
    }
}

export default Routes;