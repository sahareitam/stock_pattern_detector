import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './Layout.jsx'
import Home from './Pages/home.jsx'
import Dashboard from './Pages/Dashboard.jsx'
import { ToastProvider } from './components/ui/use-toast.jsx'
import './index.css'

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout currentPageName="Home"><Home /></Layout>,
  },
  {
    path: "/dashboard",
    element: <Layout currentPageName="Dashboard"><Dashboard /></Layout>,
  }
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ToastProvider>
      <RouterProvider router={router} />
    </ToastProvider>
  </React.StrictMode>
)