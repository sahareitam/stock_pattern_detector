import React from "react";
import { cn } from "../../utils";
// רכיב Card ראשי
const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border border-gray-200 bg-white text-gray-900 shadow-sm", // עיצוב בסיסי לכרטיס
      className
    )}
    {...props}
  />
));
Card.displayName = "Card";

// רכיב CardHeader לכותרת הכרטיס
const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)} // עיצוב בסיסי לכותרת
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

// רכיב CardTitle לכותרת טקסטואלית
const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight", // עיצוב בסיסי לכותרת טקסט
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

// רכיב CardContent לתוכן המרכזי של הכרטיס
const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("p-6 pt-0", className)} // עיצוב בסיסי לתוכן
    {...props}
  />
));
CardContent.displayName = "CardContent";

// רכיב CardFooter לחלק התחתון של הכרטיס
const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)} // עיצוב בסיסי לחלק תחתון
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardTitle, CardContent, CardFooter };