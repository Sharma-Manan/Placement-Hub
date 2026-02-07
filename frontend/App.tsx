import React, { useState, useEffect } from 'react';
import { HashRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Header from './components/Header';

// Layout wrapper to handle headers conditionally
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const isAuthPage = ['/login', '/register'].includes(location.pathname);
  
  // Login/Register have their own internal headers or different layouts in the mockups.
  // The Dashboard and Profile share a common "App Header".
  // We will handle specific page layouts inside the pages themselves to match the mocks exactly,
  // but we can manage global theme state here if needed.
  
  return (
    <div className="min-h-screen flex flex-col font-display">
      {children}
    </div>
  );
};

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleTheme = () => setDarkMode(!darkMode);

  return (
    <HashRouter>
      <AppLayout>
        <Routes>
          <Route path="/login" element={<Login toggleTheme={toggleTheme} isDark={darkMode} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard toggleTheme={toggleTheme} isDark={darkMode} />} />
          <Route path="/profile" element={<Profile toggleTheme={toggleTheme} isDark={darkMode} />} />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </AppLayout>
    </HashRouter>
  );
};

export default App;