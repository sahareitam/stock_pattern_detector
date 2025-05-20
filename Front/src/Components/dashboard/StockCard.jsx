import React from "react";
import { motion } from "framer-motion";
import { CheckCircle, XCircle, Clock, ArrowUpRight, Loader2 } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardFooter } from "../ui/LocalCard";

// Mock logos - in a real app you would use actual company logos
const stockLogos = {
  AAPL: "https://cdn-icons-png.flaticon.com/512/0/747.png",
  MSFT: "https://cdn-icons-png.flaticon.com/512/732/732221.png",
  GOOGL: "https://cdn-icons-png.flaticon.com/512/2991/2991148.png",
  AMZN: "https://logodownload.org/wp-content/uploads/2014/04/amazon-logo-0.png",
  TSLA: "https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png",
  META: "https://cdn-icons-png.flaticon.com/512/5968/5968764.png",
  NVDA: "https://cdn-icons-png.flaticon.com/512/5969/5969207.png"
};

// Mock company names
const companyNames = {
  AAPL: "Apple Inc.",
  MSFT: "Microsoft Corp.",
  GOOGL: "Alphabet Inc.",
  AMZN: "Amazon.com Inc.",
  TSLA: "Tesla Inc.",
  META: "Meta Platforms Inc.",
  NVDA: "NVIDIA Corp."
};

export default function StockCard({ symbol, status, isChecking, onCheck }) {
  const getStatusDisplay = () => {
    if (isChecking) {
      return {
        icon: <Loader2 className="h-5 w-5 animate-spin text-blue-500" />,
        text: "Checking...",
        bg: "bg-blue-50",
        textColor: "text-blue-700"
      };
    }

    if (status === null) {
      return {
        icon: <Clock className="h-5 w-5 text-gray-400" />,
        text: "Not checked",
        bg: "bg-gray-50",
        textColor: "text-gray-500"
      };
    }

    if (status === true) {
      return {
        icon: <CheckCircle className="h-5 w-5 text-emerald-500" />,
        text: "Pattern detected",
        bg: "bg-emerald-50",
        textColor: "text-emerald-700"
      };
    }
    if (status === 'error') {
        return {
            icon: <XCircle className="h-5 w-5 text-orange-500" />,
            text: "Check error",
            bg: "bg-orange-50",
            textColor: "text-orange-700"
        };
    }

    return {
      icon: <XCircle className="h-5 w-5 text-red-500" />,
      text: "No pattern detected",
      bg: "bg-red-50",
      textColor: "text-red-700"
    };
  };

  const statusDisplay = getStatusDisplay();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ translateY: -4 }}
    >
      <Card className="overflow-hidden border-gray-200 hover:border-gray-300 transition-all duration-300 shadow-sm hover:shadow">
        <div className="p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden p-1">
              <img
                src={stockLogos[symbol]}
                alt={`${symbol} logo`}
                className="w-full h-full object-contain"
              />
            </div>
            <div>
              <h3 className="font-medium text-lg">{symbol}</h3>
              <p className="text-sm text-gray-500">{companyNames[symbol]}</p>
            </div>
          </div>

          <div className={`flex items-center mt-6 py-2 px-3 rounded-md ${statusDisplay.bg}`}>
            {statusDisplay.icon}
            <span className={`text-sm ml-2 ${statusDisplay.textColor}`}>
              {statusDisplay.text}
            </span>
          </div>
        </div>

        <CardFooter className="bg-gray-50 py-3 px-6">
          <Button
            className="w-full"
            variant={status === null ? "default" : "outline"}
            disabled={isChecking}
            onClick={onCheck}
          >
            {isChecking ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Checking...
              </>
            ) : (
              <>
                <ArrowUpRight className="h-4 w-4 mr-2" />
                {status === null ? "Check Pattern" : "Check Again"}
              </>
            )}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}