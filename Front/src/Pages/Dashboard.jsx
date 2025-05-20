import React, { useState } from "react";
import { Separator } from "../components/ui/separator";
import { useToast } from "../components/ui/use-toast";
import StockCard from "../components/dashboard/StockCard";

const API_BASE_URL = "http://localhost:5000";


export default function Dashboard() {
  const { toast } = useToast();
  const [stockResults, setStockResults] = useState({
    AAPL: null,
    MSFT: null,
    GOOGL: null,
    AMZN: null,
    TSLA: null,
    META: null,
    NVDA: null
  });

  const [isChecking, setIsChecking] = useState({});

   const checkPattern = async (symbol) => {
    setIsChecking(prev => ({ ...prev, [symbol]: true }));

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const res = await fetch(`${API_BASE_URL}/api/pattern?symbol=${symbol}`, {
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        throw new Error(`API responded ${res.status}`);
      }

      const { pattern_detected } = await res.json();

      setStockResults(prev => ({ ...prev, [symbol]: pattern_detected }));
      toast({
        title: pattern_detected
          ? "Cup & Handle Pattern Detected"
          : "No Pattern Detected",
        description: `Finished analyzing ${symbol}.`,
        variant: pattern_detected ? "default" : "destructive",
      });

    } catch (err) {
      console.error(`Pattern check failed for ${symbol}:`, err);

      toast({
        title: "Error",
        description: `Could not reach the server or received an invalid response.`,
        variant: "destructive",
      });

      setStockResults(prev => ({ ...prev, [symbol]: null }));
    } finally {
      setIsChecking(prev => ({ ...prev, [symbol]: false }));
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Pattern Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Analyze stock symbols to detect Cup & Handle patterns
        </p>
      </div>

      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium">Supported Stock Symbols</h2>
      </div>

      <Separator />

      {/* Stock Cards Grid */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Object.keys(stockResults).map((symbol) => (
          <StockCard
            key={symbol}
            symbol={symbol}
            status={stockResults[symbol]}
            isChecking={isChecking[symbol]}
            onCheck={() => checkPattern(symbol)}
          />
        ))}
      </div>
    </div>
  );
}