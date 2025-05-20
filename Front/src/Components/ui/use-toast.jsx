import React, { createContext, useContext, useState } from "react";

const ToastContext = createContext({
  toast: () => {},
});

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const toast = ({ title, description, variant = "default" }) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast = {
      id,
      title,
      description,
      variant,
    };

    setToasts((prev) => [...prev, newToast]);

    // Automatically remove toast after 3 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}

      {/* Toast container */}
      <div className="fixed bottom-0 right-0 z-50 flex flex-col gap-2 p-4 max-w-md">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`bg-white border rounded-md shadow-md p-4 transition-all ${
              t.variant === "destructive" ? "border-red-500" : "border-gray-200"
            }`}
          >
            {t.title && <h4 className="font-medium mb-1">{t.title}</h4>}
            {t.description && <p className="text-gray-600 text-sm">{t.description}</p>}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}