import React, { useState, useRef, useEffect } from 'react';
import Form from '../components/Form';
import Loader from '../components/Loader';
import ResultCard from '../components/ResultCard';
import { analyzeCrop } from '../services/api';
import { TrendingUp, Bug, Bot, RefreshCcw, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    if (results && resultsRef.current) {
      // Smooth scroll to results once they are loaded
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [results]);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await analyzeCrop(formData);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getPestColor = (confidence) => {
    if (confidence < 40) return 'text-emerald-700 bg-emerald-100 border border-emerald-200';
    if (confidence < 75) return 'text-yellow-700 bg-yellow-100 border border-yellow-200';
    return 'text-rose-700 bg-rose-100 border border-rose-200';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Crop Analysis Dashboard</h1>
        <p className="text-lg text-gray-600 mt-3 max-w-2xl mx-auto">
          Enter your farm details and upload a crop image. Our AI will analyze the data and provide actionable insights.
        </p>
      </div>
      
      {error && (
        <div className="max-w-3xl mx-auto mb-8 bg-rose-50 border border-rose-200 text-rose-700 px-6 py-4 rounded-2xl flex items-start gap-4 shadow-sm animate-in slide-in-from-top-4">
          <AlertCircle className="w-6 h-6 shrink-0 mt-0.5 text-rose-500" />
          <div>
            <h3 className="font-bold text-rose-900">Analysis Failed</h3>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-sm border border-gray-100 p-12 transition-all">
          <Loader message="Analyzing your crop image and farm parameters... Please wait." />
        </div>
      ) : !results ? (
        <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-sm border border-gray-100 p-6 md:p-10 transition-all">
          <Form onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      ) : (
        <div ref={resultsRef} className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700 pt-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Analysis Results</h2>
              <p className="text-gray-500 mt-1">AI-generated insights for your maize crop.</p>
            </div>
            <button 
              onClick={handleReset}
              className="flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold rounded-xl text-gray-700 bg-white border border-gray-200 hover:bg-gray-50 hover:text-gray-900 transition-all shadow-sm hover:shadow active:scale-95 w-full sm:w-auto"
            >
              <RefreshCcw className="w-4 h-4" />
              Analyze Another Crop
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <ResultCard title="Yield Prediction" icon={TrendingUp} className="bg-gradient-to-br from-white to-blue-50/80">
              <div className="flex items-baseline gap-2">
                <span className="text-6xl font-black text-gray-900 tracking-tighter drop-shadow-sm">{results.yield_prediction.toFixed(2)}</span>
                <span className="text-xl font-bold text-gray-500">t/ha</span>
              </div>
              <p className="text-sm text-gray-500 mt-6 leading-relaxed">
                Estimated yield based on requested parameters and current visual health.
              </p>
            </ResultCard>

            <ResultCard title="Pest & Disease Detection" icon={Bug} className="bg-gradient-to-br from-white to-rose-50/80">
              <div className="flex items-center gap-4 h-full">
                <div className="flex-1">
                  <div className="text-3xl font-bold text-gray-900 capitalize break-words leading-tight">
                    {results.detected_pest.replace(/_/g, ' ')}
                  </div>
                  <div className="flex items-center gap-2 mt-6">
                    <span className={`text-sm font-bold px-4 py-1.5 rounded-full ${getPestColor(results.detection_confidence)}`}>
                      {results.detection_confidence.toFixed(1)}% Confidence
                    </span>
                  </div>
                </div>
              </div>
            </ResultCard>
          </div>

          <ResultCard title="Personalized AI Advisory" icon={Bot} className="bg-gradient-to-br from-white to-maize-50/80">
            <div className="prose prose-maize max-w-none bg-white/60 rounded-2xl p-6 md:p-8 border border-white max-h-[500px] overflow-y-auto shadow-inner text-gray-700">
              {results.advisory.split('\n').map((paragraph, idx) => {
                if (!paragraph.trim()) return null;
                // Add minor formatting for bullet points if they exist in the raw text
                if (paragraph.trim().startsWith('-') || paragraph.trim().startsWith('*')) {
                  return <li key={idx} className="ml-4 mb-2">{paragraph.replace(/^[-*]\s*/, '')}</li>;
                }
                return <p key={idx} className="mb-4 last:mb-0 leading-relaxed">{paragraph}</p>;
              })}
            </div>
          </ResultCard>
        </div>
      )}
    </div>
  );
}
