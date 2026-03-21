import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Sprout } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col font-sans bg-gray-50 text-gray-900 selection:bg-maize-200 selection:text-maize-900">
      {/* Navbar */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="p-2 bg-maize-50 rounded-xl group-hover:bg-maize-100 transition-colors">
                <Sprout className="w-6 h-6 text-maize-600" />
              </div>
              <span className="font-extrabold text-xl tracking-tight text-gray-900">
                Maize AI<span className="text-maize-600">.</span>
              </span>
            </Link>
            <nav className="flex items-center gap-1">
              <Link 
                to="/" 
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  location.pathname === '/' ? "bg-maize-50 text-maize-700" : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                )}
              >
                Home
              </Link>
              <Link 
                to="/dashboard" 
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  location.pathname === '/dashboard' ? "bg-maize-50 text-maize-700" : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                )}
              >
                Dashboard
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 mt-auto">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 text-gray-500 hover:text-maize-600 transition-colors">
            <Sprout className="w-5 h-5" />
            <span className="font-medium tracking-tight">Maize AI</span>
          </div>
          <p className="text-gray-400 text-sm">
            &copy; {new Date().getFullYear()} Smart Farming powered by AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
