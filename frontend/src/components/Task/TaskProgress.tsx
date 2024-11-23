import { Task } from '../../types/models';

interface TaskProgressProps {
  tasks: Task[];
}

export const TaskProgress = ({ tasks }: TaskProgressProps) => {
  const total = tasks.length;
  const completed = tasks.filter(task => task.status === 'completed').length;
  const inProgress = tasks.filter(task => task.status === 'in_progress').length;
  
  const completedPercentage = total ? (completed / total) * 100 : 0;
  const inProgressPercentage = total ? (inProgress / total) * 100 : 0;

  return (
    <div className="bg-white shadow sm:rounded-lg p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Progress</h2>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">
              Tasks Progress ({completed}/{total} completed)
            </span>
            <span className="text-sm font-medium text-gray-700">
              {Math.round(completedPercentage)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div className="flex h-2.5 rounded-full">
              <div 
                className="bg-green-600 rounded-l-full"
                style={{ width: `${completedPercentage}%` }}
              />
              <div 
                className="bg-yellow-400"
                style={{ width: `${inProgressPercentage}%` }}
              />
            </div>
          </div>
        </div>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-600 rounded-full"/>
            <span>Completed ({completed})</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-yellow-400 rounded-full"/>
            <span>In Progress ({inProgress})</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-gray-200 rounded-full"/>
            <span>Pending ({total - completed - inProgress})</span>
          </div>
        </div>
      </div>
    </div>
  );
};