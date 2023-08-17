import React from 'react'
import { Navigate, Outlet } from 'react-router-dom';

const Privateroute = () => {
    const token = JSON.parse(localStorage.getItem('token'));
    console.log(token)
    if (token) {
        // If token exists, the user is authenticated
        // The child routes (defined inside the PrivateRoute in your Routes configuration) will be rendered
        return <Outlet />;
    }

    // If no token is found, navigate to login
    return <Navigate to="/login" replace />;
}

export default Privateroute