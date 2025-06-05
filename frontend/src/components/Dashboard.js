import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import UserForm from './UserForm';
import UserList from './UserList';
import DownloadCSVButton from './DownloadCSVButton';

import apiService from '../services/apiService';

const Dashboard = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [usersPerPage] = useState(5);
  const { logout, user } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await apiService.getUsers();
      setUsers(response.data.data || []);
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Error al cargar los usuarios');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      const response = await apiService.createUser(userData);
      if (response.data.data) {
        setUsers(prev => [...prev, response.data.data]);
        setShowForm(false);
        setError('');
      }
    } catch (error) {
      console.error('Error creating user:', error);
      throw new Error(error.response?.data?.error || 'Error al crear usuario');
    }
  };

  const handleUpdateUser = async (userData) => {
    try {
      const response = await apiService.updateUser(editingUser.id, userData);
      if (response.data.data) {
        setUsers(prev => prev.map(user =>
          user.id === editingUser.id ? response.data.data : user
        ));
        setEditingUser(null);
        setShowForm(false);
        setError('');
      }
    } catch (error) {
      console.error('Error updating user:', error);
      throw new Error(error.response?.data?.error || 'Error al actualizar usuario');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
      try {
        await apiService.deleteUser(userId);
        setUsers(prev => prev.filter(user => user.id !== userId));
        setError('');
      } catch (error) {
        console.error('Error deleting user:', error);
        setError('Error al eliminar usuario');
      }
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingUser(null);
  };

  // Lógica de paginación
  const indexOfLastUser = currentPage * usersPerPage;
  const indexOfFirstUser = indexOfLastUser - usersPerPage;
  const currentUsers = users.slice(indexOfFirstUser, indexOfLastUser);
  const totalPages = Math.ceil(users.length / usersPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Gestión de Usuarios
              </h1>
              {user && (
                <p className="mt-1 text-sm text-gray-600">
                  Bienvenido, {user.first_name} {user.last_name}
                </p>
              )}
            </div>
            <button
              onClick={logout}
              className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
              <span className="block sm:inline">{error}</span>
              <button
                className="absolute top-0 bottom-0 right-0 px-4 py-3"
                onClick={() => setError('')}
              >
                <span className="sr-only">Cerrar</span>
                ×
              </button>
            </div>
          )}

          {!showForm ? (
            <div>
              {/* Actions Bar */}
              <div className="mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Lista de Usuarios ({users.length})
                </h2>
                <div className="flex flex-col sm:flex-row gap-3">
                  <DownloadCSVButton />
                  <button
                    onClick={() => setShowForm(true)}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  >
                    + Crear Usuario
                  </button>
                </div>
              </div>

              {/* User List */}
              <UserList
                users={currentUsers}
                loading={loading}
                onEdit={handleEditUser}
                onDelete={handleDeleteUser}
              />

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-6 flex items-center justify-between">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button
                      onClick={() => paginate(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => paginate(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Siguiente
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        Mostrando{' '}
                        <span className="font-medium">{indexOfFirstUser + 1}</span>
                        {' '}a{' '}
                        <span className="font-medium">
                          {Math.min(indexOfLastUser, users.length)}
                        </span>
                        {' '}de{' '}
                        <span className="font-medium">{users.length}</span>
                        {' '}usuarios
                      </p>
                    </div>
                    <div>
                      <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                        <button
                          onClick={() => paginate(currentPage - 1)}
                          disabled={currentPage === 1}
                          className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          ‹
                        </button>
                        {[...Array(totalPages)].map((_, index) => (
                          <button
                            key={index + 1}
                            onClick={() => paginate(index + 1)}
                            className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${currentPage === index + 1
                              ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                              }`}
                          >
                            {index + 1}
                          </button>
                        ))}
                        <button
                          onClick={() => paginate(currentPage + 1)}
                          disabled={currentPage === totalPages}
                          className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          ›
                        </button>
                      </nav>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <UserForm
              user={editingUser}
              onSubmit={editingUser ? handleUpdateUser : handleCreateUser}
              onCancel={handleCloseForm}
            />
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;