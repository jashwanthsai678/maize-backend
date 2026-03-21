import React, { useCallback, useState } from 'react';
import { UploadCloud, Image as ImageIcon, X } from 'lucide-react';

export default function ImageUpload({ onImageSelect, selectedImage }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onImageSelect(e.dataTransfer.files[0]);
    }
  }, [onImageSelect]);

  const handleChange = function(e) {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onImageSelect(e.target.files[0]);
    }
  };

  const removeImage = (e) => {
    e.stopPropagation();
    onImageSelect(null);
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-gray-900 mb-2">Crop Image <span className="text-red-500">*</span></label>
      {!selectedImage ? (
        <label
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          htmlFor="file-upload"
          className={`relative flex flex-col items-center justify-center w-full min-h-[240px] border-2 border-dashed rounded-3xl cursor-pointer transition-all duration-200 ${isDragging ? 'border-maize-500 bg-maize-50 scale-[1.02]' : 'border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-gray-400'}`}
        >
          <div className="flex flex-col items-center justify-center pt-5 pb-6 pointer-events-none">
            <div className={`p-4 rounded-full mb-4 ${isDragging ? 'bg-maize-100 text-maize-600' : 'bg-white shadow-sm text-gray-400 border border-gray-100'}`}>
              <UploadCloud className="w-8 h-8" />
            </div>
            <p className="mb-2 text-base text-gray-600">
              <span className="font-semibold text-maize-600">Click to upload</span> or drag and drop
            </p>
            <p className="text-sm text-gray-400">Supported formats: JPG, PNG, WEBP (Max 5MB)</p>
          </div>
          <input 
            id="file-upload"
            type="file" 
            className="hidden" 
            accept="image/*"
            onChange={handleChange}
          />
        </label>
      ) : (
        <div className="relative border border-gray-200 rounded-3xl overflow-hidden bg-white shadow-sm group">
          <img 
            src={URL.createObjectURL(selectedImage)} 
            alt="Selected crop" 
            className="w-full h-56 object-cover object-center"
          />
          <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-full p-1 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              type="button"
              onClick={removeImage}
              className="p-1.5 rounded-full hover:bg-red-50 text-gray-600 hover:text-red-500 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="absolute bottom-0 inset-x-0 bg-white/80 backdrop-blur-md border-t border-gray-100/50 p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-maize-50 rounded-lg text-maize-600">
                <ImageIcon className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-gray-900 truncate">{selectedImage.name}</p>
                <p className="text-xs text-gray-500">{(selectedImage.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
