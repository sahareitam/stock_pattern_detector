import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { createPageUrl } from "./utils.js";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, BarChart2, Home, AlertCircle, X } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export default function Layout({ children, currentPageName }) {
  const [isBackendHealthy, setIsBackendHealthy] = useState(true);
  const [showHealthAlert, setShowHealthAlert] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/health`, {
          signal: AbortSignal.timeout(10000)
        });

        if (res.ok) {
          setIsBackendHealthy(true);
          setShowHealthAlert(false);
        } else {
          throw new Error(`Status ${res.status}`);
        }
      } catch (err) {
        console.error("Health check failed:", err);
        setIsBackendHealthy(false);
        setShowHealthAlert(true);
      }
    };

    const id = setInterval(checkHealth, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Health Alert Banner */}
      <AnimatePresence>
        {showHealthAlert && !isBackendHealthy && (
          <motion.div
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -50, opacity: 0 }}
            className="bg-red-500 text-white py-2 px-4 flex items-center justify-between"
          >
            <div className="flex items-center">
              <AlertCircle className="w-4 h-4 mr-2" />
              <span>Backend service is currently unavailable. Results may be affected.</span>
            </div>
            <button
              onClick={() => setShowHealthAlert(false)}
              className="text-white hover:text-red-100"
            >
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <header className="bg-white border-b border-gray-200 py-3 px-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-1">
            <Activity className="h-6 w-6 text-emerald-600" />
            <span className="text-lg font-medium text-gray-900">Stock Pattern Detector</span>
          </div>
          <nav className="flex space-x-1">
            <NavLink
              to="Home"
              isActive={currentPageName === "Home"}
              icon={<Home className="h-4 w-4" />}
            >
              Home
            </NavLink>
            <NavLink
              to="Dashboard"
              isActive={currentPageName === "Dashboard"}
              icon={<BarChart2 className="h-4 w-4" />}
            >
              Dashboard
            </NavLink>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <p className="text-sm text-gray-500">
            Stock Pattern Detector • Technical Review Tool
          </p>
          <div className="flex items-center">
            <span className="text-sm text-gray-600 mr-2">Backend Status:</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              isBackendHealthy 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {isBackendHealthy ? 'Healthy' : 'Unhealthy'}
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function NavLink({ children, to, isActive, icon }) {
  return (
    <Link
      to={createPageUrl(to)}
      className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
        isActive
          ? 'text-emerald-700 bg-emerald-50'
          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
      }`}
    >
      <span className="mr-1.5">{icon}</span>
      {children}
    </Link>
  );
}