import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Leaf, ShieldCheck, TrendingUp, Cpu } from 'lucide-react';

export default function Home() {
  return (
    <div className="relative">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10 bg-gray-50">
        <div className="absolute -top-[20%] -right-[10%] w-[70%] h-[70%] rounded-full bg-maize-100/50 blur-3xl opacity-50" />
        <div className="absolute top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-blue-100/50 blur-3xl opacity-50" />
      </div>

      {/* Hero Section */}
      <section className="pt-20 md:pt-32 pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto border border-gray-100 bg-white/40 backdrop-blur-3xl rounded-3xl p-8 md:p-16 shadow-xl shadow-gray-200/20">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-maize-50 border border-maize-100 text-maize-700 text-sm font-semibold mb-8">
            <Cpu className="w-4 h-4" />
            <span>AI-Powered Agriculture</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 tracking-tight leading-[1.1] mb-8">
            Smart farming <br/>powered by <span className="text-maize-600 bg-clip-text text-transparent bg-gradient-to-r from-maize-600 to-emerald-500">AI</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            Upload an image of your maize crop to get instant pest detection, yield predictions, and personalized advisory to maximize your harvest.
          </p>
          <div className="flex justify-center">
            <Link 
              to="/dashboard" 
              className="group inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-2xl text-white bg-maize-600 hover:bg-maize-700 shadow-lg shadow-maize-600/30 hover:shadow-xl hover:shadow-maize-600/40 transition-all hover:-translate-y-1 w-full sm:w-auto"
            >
              Analyze Crop Now
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-12">
            {[
              {
                icon: ShieldCheck,
                title: 'Pest & Disease Detection',
                desc: 'Instantly identify potential threats to your crop through advanced image analysis.',
                color: 'text-rose-500',
                bg: 'bg-rose-50'
              },
              {
                icon: TrendingUp,
                title: 'Yield Prediction',
                desc: 'Accurately forecast your harvest based on field parameters and visual health.',
                color: 'text-blue-500',
                bg: 'bg-blue-50'
              },
              {
                icon: Leaf,
                title: 'AI Advisory',
                desc: 'Receive actionable, step-by-step guidance to treat issues and optimize growth.',
                color: 'text-maize-600',
                bg: 'bg-maize-50'
              }
            ].map((feature, idx) => (
              <div key={idx} className="flex flex-col items-start p-6 rounded-3xl hover:bg-gray-50 transition-colors">
                <div className={`w-14 h-14 ${feature.bg} rounded-2xl flex items-center justify-center mb-6`}>
                  <feature.icon className={`w-7 h-7 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
