import axios from 'axios';

// Replace with actual backend IP or use environment variable
// We default to a placeholder that the user can replace
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const analyzeCrop = async (formDataObj) => {
  const formData = new FormData();
  formData.append('district', formDataObj.district);
  formData.append('season', formDataObj.season);
  formData.append('crop_year', Number(formDataObj.crop_year));
  formData.append('area_ha', Number(formDataObj.area_ha));
  formData.append('growth_stage', formDataObj.growth_stage);
  formData.append('language', formDataObj.language);
  formData.append('image', formDataObj.image);

  try {
    const response = await axios.post(`${API_BASE_URL}/process_all`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error(error.response?.data?.detail || 'Failed to analyze crop. Please verify the backend is running and reachable.');
  }
};
