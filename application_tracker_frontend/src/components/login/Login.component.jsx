import React from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { Card, CardContent, Typography } from "@mui/material";
import GoogleLoginButton from "./GoogleLoginButton.component";

const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const Login = () => {
  return (
    <Card sx={{ minWidth: 275 }}>
      <CardContent
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Typography variant="h4" color="text.primary" gutterBottom>
          Google Login
        </Typography>
        <GoogleOAuthProvider clientId={clientId}>
            <GoogleLoginButton/>
        </GoogleOAuthProvider>
      </CardContent>
    </Card>
  );
};

export default Login;
