import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Project, Task, User } from '../../types/models';
import { projectApi, projectMemberApi, taskApi } from '../../services/api';
import { TaskList } from '../Task/TaskList';
import { MemberList } from '../Members/MemberList';
import { TaskProgress } from '../Task/TaskProgress';


export const ProjectDetails = () => {
  const { id } = useParams();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState('');
  const [members, setMembers] = useState<User[]>([]);

  const fetchData = useCallback(async () => {
    try {
      if (!id) return;
      const [projectData, tasksData, membersData] = await Promise.all([
        projectApi.getProject(id),
        taskApi.getTasks(id),
        projectMemberApi.getProjectMembers(id)
      ]);
      setProject(projectData);
      setTasks(tasksData);
      setMembers(membersData);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch project data');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!project) return null;

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
  
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{project.title}</h1>
            <p className="mt-1 text-sm text-gray-500">{project.description}</p>
          </div>
        </div>
      </div>

      <TaskProgress tasks={tasks} />
  
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TaskList 
          projectId={id!} 
          tasks={tasks} 
          members={members}
          onTasksChange={fetchData}
        />
        <MemberList 
          projectId={id!}
          members={members}
          onMembersChange={fetchData}
        />
      </div>
    </div>
  );
};