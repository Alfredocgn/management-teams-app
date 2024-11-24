import { useState } from 'react';
import { Task, User } from '../../types/models';
import { taskApi } from '../../services/api';
import { useSubscriptionStatus } from '../../hooks/useSubscriptionStatus';
import { format } from 'date-fns';

interface TaskDetailProps {
  task: Task;
  projectId: string;
  members: User[];
  onTaskUpdate: () => void;
  onClose: () => void;
}

export const TaskDetail = ({ task, projectId, members, onTaskUpdate, onClose }: TaskDetailProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description);
  const [status, setStatus] = useState(task.status);
  const [assigneeId, setAssigneeId] = useState(task.assignee_id);
  const [dueDate, setDueDate] = useState(task.due_date ? format(new Date(task.due_date), 'yyyy-MM-dd') : '');
  const { isSubscribed } = useSubscriptionStatus();

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await taskApi.deleteTask(projectId, task.id);
        onTaskUpdate();
        onClose();
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await taskApi.updateTask(projectId, task.id, {
        title,
        description,
        status,
        assignee_id: assigneeId,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
      });
      onTaskUpdate();
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        {isEditing && isSubscribed ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-2 border rounded"
              required
            />
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2 border rounded"
              rows={4}
            />
            <div className="grid grid-cols-2 gap-4">
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as Task['status'])}
                className="p-2 border rounded"
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
              <select
                value={assigneeId || ''}
                onChange={(e) => setAssigneeId(e.target.value || null)}
                className="p-2 border rounded"
              >
                <option value="">Unassigned</option>
                {members.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.first_name} {member.last_name}
                  </option>
                ))}
              </select>
            </div>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full p-2 border rounded"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 text-gray-600 border rounded hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Save
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-start">
              <h2 className="text-xl font-bold">{task.title}</h2>
              <div className="flex gap-2">
                {isSubscribed && (
                  <>
                    <button
                      onClick={() => setIsEditing(true)}
                      className="px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50"
                    >
                      Edit
                    </button>
                    <button
                      onClick={handleDelete}
                      className="px-3 py-1 text-red-600 border border-red-600 rounded hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </>
                )}
                <button
                  onClick={onClose}
                  className="px-3 py-1 text-gray-600 border rounded hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </div>
            <p className="text-gray-600">{task.description}</p>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-semibold">Status:</span> {task.status}
              </div>
              <div>
                <span className="font-semibold">Assignee:</span>{' '}
                {members.find((m) => m.id === task.assignee_id)?.first_name || 'Unassigned'}
              </div>
              <div>
                <span className="font-semibold">Due Date:</span>{' '}
                {task.due_date ? format(new Date(task.due_date), 'PPP') : 'No due date'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};