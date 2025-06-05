import React, { useState } from 'react';
import apiService from '../services/apiService';

const DownloadCSVButton = () => {
  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async () => {
    try {
      setIsLoading(true);
      await apiService.downloadUsersCSV();
    } catch (error) {
      console.error('Error al descargar CSV:', error);
      alert('Error al descargar el archivo CSV');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={isLoading}
      className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
    >
      {isLoading ? (
        <span>Descargando...</span>
      ) : (
        <span>Descargar CSV</span>
      )}
    </button>
  );
};

export default DownloadCSVButton;