import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import React from "react";
import { useNavigate } from "react-router-dom";
const apiUrl = process.env.REACT_APP_API_URL;
const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

export const Authentication = () => {

  const navigate = useNavigate()
  const onSuccess = async (credentialResponse) => {
    console.log(apiUrl)
    const response = await fetch(`${apiUrl}auth/callback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentialResponse),
    });

    const data = await response.json();
    const token = data.token;
    localStorage.setItem('token',JSON.stringify(token))
    navigate("/dashboard")
  };
  return (
    <div>
      <GoogleOAuthProvider clientId={clientId}>
        <GoogleLogin
          onSuccess={(credentialResponse) => onSuccess(credentialResponse)}
          onError={() => {
            console.log("Login Failed");
          }}
          useOneTap
        />
      </GoogleOAuthProvider>
      ;
    </div>
  );
};

export default Authentication;
