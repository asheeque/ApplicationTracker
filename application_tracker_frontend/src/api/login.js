import axios from "axios";
const apiUrl = process.env.REACT_APP_API_URL;

export const fetchGoogleAuth = async ({ codeResponse }) => {
  const headers = {
    "Content-Type": "application/json",
  };
  const body = JSON.stringify({
    ...codeResponse,
  });
  const response = await axios.post(`${apiUrl}auth/google`, body, { headers });
  const data = await response.data;
  return data;
};
