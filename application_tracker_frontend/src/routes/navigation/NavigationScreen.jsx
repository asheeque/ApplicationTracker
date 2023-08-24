import React from "react";
import { Outlet } from "react-router-dom";
import Navigation from "../../components/navigation/Navigation.component";

const NavigationScreen = () => {
  return (
    <>
      <Navigation />
      <Outlet />
    </>
  );
};

export default NavigationScreen;
