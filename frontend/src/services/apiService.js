import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para manejar respuestas
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.api.post('/api/token/refresh/', {
                refresh: refreshToken,
              });

              const { access } = response.data;
              localStorage.setItem('access_token', access);
              this.setAuthToken(access);

              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Si el refresh falla, limpiar tokens y redirigir al login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token) {
    if (token) {
      this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.api.defaults.headers.common['Authorization'];
    }
  }

  // Autenticación
  async login(email, password) {
    return this.api.post('/api/token/', { email, password });
  }

  // Usuarios
  async getUsers() {
    return this.api.get('/api/v1/users/');
  }

  async createUser(userData) {
    return this.api.post('/api/v1/users/', userData);
  }

  async updateUser(id, userData) {
    return this.api.put(`/api/v1/users/${id}/`, userData);
  }

  async deleteUser(id) {
    return this.api.delete(`/api/v1/users/${id}/`);
  }

  // Descargar el CSV de usuarios
  async downloadUsersCSV() {
    try {
      const response = await this.api.get('/api/v1/users/export/csv/', {
        responseType: 'blob',
        headers: {
          'Accept': 'text/csv',
        }
      });

      // Verificar que la respuesta sea realmente un CSV
      if (response.headers['content-type'] && response.headers['content-type'].includes('text/csv')) {
        // Crear un objeto URL para el blob
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));

        // Crear un elemento <a> temporal
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'users.csv');

        // Agregar al DOM y hacer clic
        document.body.appendChild(link);
        link.click();

        // Limpiar
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        return true;
      } else {
        throw new Error('El servidor no devolvió un archivo CSV válido');
      }
    } catch (error) {
      console.error('Error downloading CSV:', error);
      throw error;
    }
  }
}

const apiService = new ApiService();
export default apiService;