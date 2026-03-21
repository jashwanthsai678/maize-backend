import React from 'react';

export default function ResultCard({ title, icon: Icon, children, className = '' }) {
  return (
    <div className={`bg-white rounded-3xl p-6 md:p-8 shadow-sm border border-gray-100 hover:shadow-md transition-shadow ${className}`}>
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-gray-50 rounded-2xl text-gray-700 shadow-inner">
          <Icon className="w-6 h-6" />
        </div>
        <h3 className="text-xl font-bold text-gray-900 tracking-tight">{title}</h3>
      </div>
      <div>
        {children}
      </div>
    </div>
  );
}
