import './App.css';
import Navigation from './routes/navigation/NavigationScreen';
import Authentication from './routes/authentication/AuthenticationScreen';
import { Navigate, Route, Routes } from 'react-router-dom';
import Privateroute from './routes/authentication/Privateroute.component';
import Dashboard from './routes/dashboard/DashboardScreen';
import Home from './routes/home/Home.component';

function App() {
  const token = localStorage.getItem('token');

  return (
    <Routes>
      <Route path="/" element={<Navigation />}>
        <Route index element={<Home/>}/>
        <Route path='login' element={<Authentication />} />
        <Route path="dashboard" element={<Privateroute />}>
          <Route index element={<Dashboard />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
