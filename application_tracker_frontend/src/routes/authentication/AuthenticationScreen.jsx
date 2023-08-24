import { Box, Container } from "@mui/material";
import React from "react";
import Login from "../../components/login/Login.component";
import styles from "./AuthenticationScreen.module.css"
export const AuthenticationScreen = () => {
  return (
    <React.Fragment>
      <Container  className={styles.container}>
        {/* <Box > */}
          <Login />
        {/* </Box> */}
      </Container>
    </React.Fragment>
  );
};

export default AuthenticationScreen;
