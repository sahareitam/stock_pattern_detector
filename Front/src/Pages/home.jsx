import React from "react";
import { Link } from "react-router-dom";
import { createPageUrl } from "../utils.js";
import { motion } from "framer-motion";
import { Activity, ArrowRight, BarChart2 } from "lucide-react";
import { Button } from "../Components/ui/button.jsx";

export default function Home() {
  return (
    <div className="flex flex-col space-y-12">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <div className="inline-flex items-center justify-center p-2 bg-emerald-50 rounded-full mb-8">
          <Activity className="h-8 w-8 text-emerald-600" />
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          Stock Pattern Detector
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600 max-w-3xl mx-auto">
          A technical review tool for evaluating algorithmic pattern detection in financial data.
          Analyze stock patterns and validate detection capabilities in real-time.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link to={createPageUrl("Dashboard")}>
            <Button className="bg-emerald-600 hover:bg-emerald-700">
              Go to Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </motion.div>

      {/* Pattern Explanation */}
      <motion.section
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="bg-white rounded-xl shadow-sm overflow-hidden max-w-4xl mx-auto"
      >
        <div className="px-6 py-8 sm:p-10">
          <div className="flex items-center mb-4">
            <div className="mr-4 flex-shrink-0 inline-flex items-center justify-center p-2 bg-blue-50 rounded-full">
              <BarChart2 className="h-6 w-6 text-blue-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Cup & Handle Pattern</h2>
          </div>

          <div className="mt-4 text-gray-600">
            <p className="mb-4">
              The Cup and Handle is a bullish continuation pattern where the price movements form a "cup" shape followed by a smaller "handle" consolidation phase.
              When the price breaks out above the handle's resistance, it often signals a continuation of the prior uptrend.
            </p>

            <p className="mb-4">
              The algorithm identifies a Cup and Handle when it sees a rounded bottom followed by a short period of consolidation before a potential breakout, analyzing multiple data points to reduce false positives.
            </p>

            <p className="text-sm text-gray-500 italic">
              The pattern detection capabilities are part of the technical assessment being evaluated through this interface.
            </p>
          </div>
        </div>
      </motion.section>
    </div>
  );
}