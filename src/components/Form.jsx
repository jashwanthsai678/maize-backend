import React, { useState } from 'react';
import ImageUpload from './ImageUpload';
import { Leaf } from 'lucide-react';

export default function Form({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    district: '',
    season: 'Kharif',
    crop_year: new Date().getFullYear(),
    area_ha: '',
    growth_stage: 'Vegetative',
    language: 'English',
    image: null
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.image) {
      alert('Please upload an image of the crop.');
      return;
    }
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageSelect = (file) => {
    setFormData(prev => ({ ...prev, image: file }));
  };

  const inputClass = "w-full rounded-2xl border-gray-200 shadow-sm focus:border-maize-500 focus:ring-maize-500 bg-gray-50 hover:bg-white focus:bg-white transition-colors text-base px-4 py-3.5 border outline-none";
  const labelClass = "block text-sm font-semibold text-gray-900 mb-2 pl-1";

  return (
    <form onSubmit={handleSubmit} className="text-left space-y-8">
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-8">
        <div>
          <label className={labelClass}>District</label>
          <input required type="text" name="district" value={formData.district} onChange={handleChange} className={inputClass} placeholder="e.g. Karimnagar" />
        </div>

        <div>
           <label className={labelClass}>Season</label>
           <select name="season" value={formData.season} onChange={handleChange} className={inputClass}>
             <option value="Kharif">Kharif</option>
             <option value="Rabi">Rabi</option>
             <option value="Summer">Summer</option>
           </select>
        </div>

        <div>
           <label className={labelClass}>Crop Year</label>
           <input required type="number" name="crop_year" value={formData.crop_year} onChange={handleChange} className={inputClass} min="2000" max="2100" />
        </div>

        <div>
           <label className={labelClass}>Area (Hectares)</label>
           <input required type="number" step="0.01" name="area_ha" value={formData.area_ha} onChange={handleChange} className={inputClass} placeholder="e.g. 2.5" />
        </div>

        <div>
           <label className={labelClass}>Growth Stage</label>
           <select name="growth_stage" value={formData.growth_stage} onChange={handleChange} className={inputClass}>
             <option value="Seedling">Seedling</option>
             <option value="Vegetative">Vegetative</option>
             <option value="Flowering">Flowering</option>
             <option value="Harvest">Harvest</option>
           </select>
        </div>

        <div>
           <label className={labelClass}>Language</label>
           <select name="language" value={formData.language} onChange={handleChange} className={inputClass}>
             <option value="English">English</option>
             <option value="Hindi">Hindi</option>
             <option value="Telugu">Telugu</option>
           </select>
        </div>
      </div>

      <div className="pt-2">
        <ImageUpload onImageSelect={handleImageSelect} selectedImage={formData.image} />
      </div>

      <div className="pt-6">
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center py-5 px-8 border border-transparent rounded-2xl shadow-lg shadow-maize-600/20 text-lg font-bold text-white bg-maize-600 hover:bg-maize-700 hover:shadow-xl hover:shadow-maize-600/30 focus:outline-none focus:ring-offset-2 focus:ring-maize-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5 active:translate-y-0"
        >
          {isLoading ? 'Processing...' : (
            <>
              <Leaf className="w-6 h-6 mr-2" />
              Analyze Crop
            </>
          )}
        </button>
      </div>
    </form>
  );
}
