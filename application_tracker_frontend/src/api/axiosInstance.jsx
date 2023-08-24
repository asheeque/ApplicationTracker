import axios from "axios";
const apiUrl = process.env.REACT_APP_API_URL;

console.log(apiUrl, "apii");
const axiosInstance = axios.create({
  baseURL: apiUrl,
});

axiosInstance.interceptors.request.use(
  (config) => {
    try {
        let token = localStorage.getItem('token');
        if (token) {
            token = token.replace(/^"|"$/g, ''); // Trimming the quotes

            config.headers.Authorization = `Bearer ${token}`;
            config.headers['Content-Type'] = 'application/json'; // Setting Content-Type to JSON

        }
        console.log('Starting Request:', config); // This line prints the request

        return config
    } catch (error) {
        console.error('Error fetching token from localStorage:', error);
    }
  },
  (err) => {
    return Promise.reject(err);
  }
);

export default axiosInstance;
