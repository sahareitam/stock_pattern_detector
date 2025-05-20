import React from "react";
import { cn } from "../../utils";

// Alert Components
const Alert = React.forwardRef(({ className, variant = "default", children, ...props }, ref) => {
  const variantClasses = {
    default: "bg-gray-100 text-gray-800",
    destructive: "bg-red-100 text-red-800",
  };

  return (
    <div
      ref={ref}
      className={cn(
        "rounded-md border p-4",
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});
Alert.displayName = "Alert";

const AlertTitle = React.forwardRef(({ className, children, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("mb-1 font-medium", className)}
    {...props}
  >
    {children}
  </h5>
));
AlertTitle.displayName = "AlertTitle";

const AlertDescription = React.forwardRef(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm", className)}
    {...props}
  >
    {children}
  </div>
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertTitle, AlertDescription };