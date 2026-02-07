import { apiRequest } from '../services/api';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface LoginProps {
  toggleTheme: () => void;
  isDark: boolean;
}

const Login: React.FC<LoginProps> = ({ toggleTheme, isDark }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');


  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError('');

  try {
    const res = await apiRequest<{
      access_token: string;
      refresh_token: string;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    localStorage.setItem('access_token', res.access_token);
    localStorage.setItem('refresh_token', res.refresh_token);

    navigate('/dashboard');
  } catch (err: any) {
    setError(err.message || 'Invalid email or password');
  }
};


  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Navigation / Header Area */}
      <header className="w-full px-6 lg:px-10 py-4 flex items-center justify-between bg-white/50 dark:bg-background-dark/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="size-8 bg-primary rounded-lg flex items-center justify-center text-white">
            <span className="material-symbols-outlined text-2xl">grid_view</span>
          </div>
          <h2 className="text-xl font-extrabold tracking-tight">PLACEMIND.AI</h2>
        </div>
        <button 
          onClick={toggleTheme}
          className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition-colors" 
          title="Toggle Theme"
        >
          <span className="material-symbols-outlined block dark:hidden">dark_mode</span>
          <span className="material-symbols-outlined hidden dark:block">light_mode</span>
        </button>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-[440px]">
          {/* Login Card */}
          <div className="bg-white dark:bg-[#251a33] rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)] border border-[#ede7f3] dark:border-[#352648] overflow-hidden">
            {/* Illustration/Header inside card */}
            <div className="h-32 bg-primary/10 dark:bg-primary/20 relative overflow-hidden flex items-center justify-center">
              <div 
                className="absolute inset-0 opacity-20" 
                style={{ backgroundImage: 'radial-gradient(#7f13ec 1px, transparent 1px)', backgroundSize: '20px 20px' }}
              >
              </div>
              <div className="relative z-10 flex flex-col items-center">
                <span className="material-symbols-outlined text-primary text-5xl">school</span>
              </div>
            </div>
            
            <div className="p-8 lg:p-10">
              <div className="mb-8">
                <h1 className="text-2xl font-bold mb-2">Student Login</h1>
                <p className="text-gray-500 dark:text-gray-400 text-sm">Enter your credentials to access your placement dashboard.</p>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <p className="text-red-500 text-sm font-medium">{error}</p>
                )}
                {/* Email Field */}
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">Email Address</label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xl">mail</span>
                    <input 
                      type="email" 
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 bg-background-light dark:bg-[#191022] border border-[#dbcfe7] dark:border-[#352648] rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all dark:text-white" 
                      placeholder="student@college.edu" 
                    />
                  </div>
                </div>
                
                {/* Password Field */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">Password</label>
                    <a href="#" className="text-xs font-semibold text-primary hover:underline">Forgot Password?</a>
                  </div>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xl">lock</span>
                    <input 
                      type="password" 
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-10 pr-12 py-3 bg-background-light dark:bg-[#191022] border border-[#dbcfe7] dark:border-[#352648] rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all dark:text-white" 
                      placeholder="••••••••" 
                    />
                    <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary transition-colors">
                      <span className="material-symbols-outlined text-xl">visibility</span>
                    </button>
                  </div>
                </div>
                
                {/* Sign In Button */}
                <button 
                  type="submit" 
                  className="w-full bg-primary hover:bg-primary/90 text-white font-bold py-3.5 rounded-lg shadow-lg shadow-primary/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2"
                >
                  Sign In
                  <span className="material-symbols-outlined text-lg">login</span>
                </button>
              </form>
              
              {/* Divider */}
              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-[#ede7f3] dark:border-[#352648]"></div>
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white dark:bg-[#251a33] px-2 text-gray-400">Security Notice</span>
                </div>
              </div>
              
              <p className="text-center text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                Accessing from a public computer? Remember to log out. <br/>
                New here? <Link to="/register" className="text-primary font-bold hover:underline">Create Account</Link>
              </p>
            </div>
          </div>
          
          {/* Footer Meta */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-400">© 2024 PLACEMIND.AI. All rights reserved.</p>
            <div className="flex justify-center gap-4 mt-2">
              <a href="#" className="text-xs text-gray-400 hover:text-primary">Privacy Policy</a>
              <a href="#" className="text-xs text-gray-400 hover:text-primary">Terms of Service</a>
            </div>
          </div>
        </div>
      </main>
      
      {/* Bottom Background Elements (Decorative) */}
      <div className="fixed bottom-0 left-0 w-full h-1 bg-gradient-to-r from-primary/10 via-primary/50 to-primary/10"></div>
    </div>
  );
};

export default Login;