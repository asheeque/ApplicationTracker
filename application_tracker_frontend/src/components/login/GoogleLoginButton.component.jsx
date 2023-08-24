import { GoogleLogin } from "@react-oauth/google";
import React from "react";
import { useNavigate } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";
import { Button } from "@mui/base";
import { fetchGoogleAuth } from "../../api/login";


const GoogleLoginButton = () => {
  const navigate = useNavigate();
  const login = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      const data = await fetchGoogleAuth({ codeResponse });
      const token = data.token;
      localStorage.setItem("token", JSON.stringify(token));
      navigate("/dashboard");
    },
    flow: "auth-code",
    scope: "https://www.googleapis.com/auth/gmail.readonly",
  });
  return <Button onClick={() => login()}>Sign in with Google 🚀 </Button>;
};

export default GoogleLoginButton;
