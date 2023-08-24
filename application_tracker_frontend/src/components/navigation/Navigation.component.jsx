import React, { useEffect } from "react";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { useLocation, useNavigate } from "react-router-dom";

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const getInitialTab = () => {
    switch (location.pathname) {
      case "/dashboard":
        return 0;
      case "/login":
        return 1;
      default:
        return 0;
    }
  };
  const [value, setValue] = React.useState(getInitialTab());

  useEffect(() => {
    const tab = () => {
      switch (location.pathname) {
        case "/dashboard":
          return 0;
        case "/login":
          return 1;
        default:
          return 0;
      }
    };
    setValue(tab);
  }, [location.pathname]);

  const handleChange = (event, newValue) => {
    setValue(newValue);
    switch (newValue) {
      case 0:
        navigate("/dashboard");
        break;
      case 1:
        navigate("/login");
        break;
      default:
        break;
    }
  };
  return (
    <Box sx={{ width: "100%", bgcolor: "background.paper" }}>
      <Tabs value={value} onChange={handleChange} centered>
        <Tab label="Item One" />
        <Tab label="Item Two" />
        <Tab label="Item Three" />
      </Tabs>
    </Box>
  );
};

export default Navigation;
