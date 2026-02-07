import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface HeaderProps {
  toggleTheme: () => void;
  isDark: boolean;
}

const Header: React.FC<HeaderProps> = ({ toggleTheme, isDark }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path 
      ? "text-primary font-bold border-b-2 border-primary py-1" 
      : "text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors";
  };

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between border-b border-solid border-[#ede7f3] dark:border-[#2d2238] bg-white/80 dark:bg-background-dark/80 backdrop-blur-md px-6 md:px-10 py-3">
      <div className="flex items-center gap-4 text-[#140d1b] dark:text-white">
        <div className="text-primary">
          <span className="material-symbols-outlined text-4xl">grid_view</span>
        </div>
        <Link to="/dashboard">
          <h2 className="text-lg font-bold leading-tight tracking-[-0.015em] font-display">PLACEMIND.AI</h2>
        </Link>
      </div>
      <div className="flex flex-1 justify-end items-center gap-4 md:gap-8">
        <nav className="hidden md:flex items-center gap-9">
          <Link to="/dashboard" className={isActive('/dashboard')}>Dashboard</Link>
          <a href="#" className="text-sm font-medium hover:text-primary transition-colors text-slate-600 dark:text-slate-300">Jobs</a>
          <Link to="/profile" className={isActive('/profile')}>Profile</Link>
          <a href="#" className="text-sm font-medium hover:text-primary transition-colors text-slate-600 dark:text-slate-300">Resources</a>
        </nav>
        
        <button 
          onClick={toggleTheme}
          className="flex size-10 items-center justify-center rounded-lg bg-[#ede7f3] dark:bg-[#2d2238] text-primary hover:bg-primary hover:text-white transition-all"
        >
          <span className="material-symbols-outlined">
            {isDark ? 'light_mode' : 'dark_mode'}
          </span>
        </button>
        
        <div 
          className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border-2 border-primary/20" 
          style={{ backgroundImage: 'url("https://picsum.photos/100/100")' }}
        >
        </div>
      </div>
    </header>
  );
};

export default Header;