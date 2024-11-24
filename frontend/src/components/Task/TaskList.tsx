import { useState } from 'react';
import { Task, User } from '../../types/models';
import { taskApi } from '../../services/api';
import { CreateTaskForm } from './CreateTaskForm';
import { useSubscriptionStatus } from '../../hooks/useSubscriptionStatus';
import { TaskDetail } from './TaskDetail';

interface TaskListProps {
  projectId: string;
  tasks: Task[];
  onTasksChange: () => void;
  members:User[]
}

export const TaskList = ({ projectId, tasks,members, onTasksChange }: TaskListProps) => {
  const [showForm, setShowForm] = useState(false);
  const { isSubscribed } = useSubscriptionStatus();
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

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
                      {isSubscribed && (
                        <button
                          onClick={() => setShowForm(!showForm)}
                          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                        >
                          {showForm ? 'Cancel' : 'Add Task'}
                        </button>
                      )}
                    </div>

                    {showForm && isSubscribed && (
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
              <div key={task.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div 

                  className="flex-1 "
                >
                  <h3 className="text-sm font-medium text-gray-900">{task.title}</h3>
                  <p className="text-sm text-gray-500">{task.description}</p>
                </div>
                {isSubscribed ? (
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
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
                    <button
                      onClick={() => setSelectedTask(task)}
                      className="px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50"
                    >
                      Edit
                    </button>
                  </div>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">
                    {task.assignee ? `${task.assignee.first_name} ${task.assignee.last_name}` : 'Unassigned'}
                  </span>
                  <span className="px-2 py-1 text-sm rounded-full bg-gray-100 text-gray-700">
                    {task.status}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      {selectedTask && (
        <TaskDetail
          task={selectedTask}
          projectId={projectId}
          members={members}
          onTaskUpdate={onTasksChange}
          onClose={() => setSelectedTask(null)}
        />
)}
    </div>
  );
};