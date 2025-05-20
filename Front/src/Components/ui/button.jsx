import React from "react";
import { cn } from "../../utils";

// Button Component
const Button = React.forwardRef(
  ({ className, variant = "default", size = "default", children, ...props }, ref) => {
    const variantClasses = {
      default: "bg-emerald-600 text-white hover:bg-emerald-700",
      destructive: "bg-red-500 text-white hover:bg-red-600",
      outline: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50",
      ghost: "bg-transparent text-gray-700 hover:bg-gray-100",
      link: "text-emerald-600 underline-offset-4 hover:underline bg-transparent",
    };

    const sizeClasses = {
      default: "h-10 px-4 py-2",
      sm: "h-8 px-3 text-sm",
      lg: "h-12 px-6",
      icon: "h-9 w-9",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button };