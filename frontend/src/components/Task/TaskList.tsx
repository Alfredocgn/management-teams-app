import { useState } from 'react';
import { Task, User } from '../../types/models';
import { taskApi } from '../../services/api';
import { CreateTaskForm } from './CreateTaskForm';

interface TaskListProps {
  projectId: string;
  tasks: Task[];
  onTasksChange: () => void;
  members:User[]
}

export const TaskList = ({ projectId, tasks,members, onTasksChange }: TaskListProps) => {
  const [showForm, setShowForm] = useState(false);

  const handleStatusChange = async (taskId: string, newStatus: Task['status']) => {
    try {
      await taskApi.updateTask(projectId, taskId, { status: newStatus });
      onTasksChange();
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  const handleAssigneeChange = async (taskId: string, assigneeId: string | null) => {
    try {

      const updateData = assigneeId === '' 
        ? { assignee_id: undefined }  
        : { assignee_id: assigneeId };
      
      await taskApi.updateTask(projectId, taskId, updateData);
      onTasksChange();
    } catch (error) {
      console.error('Failed to update task assignee:', error);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-gray-900">Tasks</h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            {showForm ? 'Cancel' : 'Add Task'}
          </button>
        </div>

        {showForm && (
          <CreateTaskForm
            projectId={projectId}
            members={members}
            onSubmit={async () => {
              setShowForm(false);
              onTasksChange();
            }}
          />
        )}
              <div className="mt-6 space-y-4">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
          >
            <div className="flex-1">
              <h3 className="text-sm font-medium text-gray-900">{task.title}</h3>
              <p className="text-sm text-gray-500">{task.description}</p>
            </div>
            <div className="flex items-center gap-2">
              <select
                  value={task.assignee_id || ''}
                  onChange={(e) => handleAssigneeChange(task.id, e.target.value || null)}
                  className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option value="">Unassigned</option>
                  {members.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.first_name} {member.last_name}
                    </option>
                  ))}
              </select>
              <select
                value={task.status}
                onChange={(e) => handleStatusChange(task.id, e.target.value as Task['status'])}
                className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
        ))}
          {tasks.length === 0 && (
            <p className="text-gray-500 text-center py-4">No tasks yet</p>
          )}
        </div>
      </div>
    </div>
  );
};