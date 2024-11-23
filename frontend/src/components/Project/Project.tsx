import { useState, useEffect } from 'react';
import { CreateProjectData, Project } from '../../types/models';
import { projectApi } from '../../services/api';
import { CreateProjectForm } from './CreateProjectForm';
import { Link } from 'react-router-dom';

export const Projects = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);

  const fetchProjects = async () => {
    try {
      const data = await projectApi.getProjects();
      setProjects(data);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (values: CreateProjectData) => {
    try {
      await projectApi.createProject(values);
      await fetchProjects();
      setShowForm(false);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create project');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Projects</h1>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          {showForm ? 'Cancel' : 'New Project'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {showForm && <CreateProjectForm onSubmit={handleCreateProject} />}
      
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {projects.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No projects yet. Create your first project!</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {projects.map((project) => (
              <li key={project.id} className="px-6 py-4 hover:bg-gray-50">
                <Link to={`/dashboard/projects/${project.id}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-medium text-gray-900">{project.title}</h2>
                      <p className="text-sm text-gray-500">{project.description}</p>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};