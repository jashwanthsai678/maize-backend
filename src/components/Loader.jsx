import React from 'react';
import { Loader2, Sprout } from 'lucide-react';

export default function Loader({ message = "Analyzing your crop... Please wait" }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4">
      <div className="relative mb-8">
        <div className="absolute inset-0 rounded-full bg-maize-200 animate-ping opacity-75"></div>
        <div className="relative bg-white rounded-full p-5 shadow-xl shadow-maize-100/50 border border-maize-50">
          <Loader2 className="w-12 h-12 text-maize-600 animate-spin" />
          <Sprout className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-5 h-5 text-maize-700" />
        </div>
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-3 tracking-tight">Processing Data</h3>
      <p className="text-gray-500 animate-pulse text-lg">{message}</p>
    </div>
  );
}
