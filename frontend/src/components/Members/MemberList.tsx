import { useState } from 'react';
import { User } from '../../types/models';
import { projectMemberApi, userApi } from '../../services/api';
import { useSubscriptionStatus } from '../../hooks/useSubscriptionStatus';

interface MemberListProps {
  projectId: string;
  members: User[];
  onMembersChange: () => void;
}

export const MemberList = ({ projectId, members, onMembersChange }: MemberListProps) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const { isSubscribed } = useSubscriptionStatus();

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const user = await userApi.searchByEmail(email);
      if (user) {
        await projectMemberApi.addProjectMember(projectId, user.id);
        setEmail('');
        setShowAddForm(false);
        onMembersChange();
      }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add member');
    }
  };
  const handleRemoveMember = async (userId: string) => {
    try {
      await projectMemberApi.removeProjectMember(projectId, userId);
      onMembersChange();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-gray-900">Team Members</h2>
          {isSubscribed && (
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              {showAddForm ? 'Cancel' : 'Add Member'}
            </button>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {showAddForm && (
          <form onSubmit={handleAddMember} className="mb-4">
            <div className="flex gap-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter email address"
                className="flex-1 rounded-md border-gray-300"
              />
              <button
                type="submit"
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Add
              </button>
            </div>
          </form>
        )}

        <div className="divide-y divide-gray-200">
          {members.map((member) => (
            <div key={member.id} className="py-4 flex justify-between items-center">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {member.first_name} {member.last_name}
                </p>
                <p className="text-sm text-gray-500">{member.email}</p>
              </div>
              {isSubscribed && (
                <button
                  onClick={() => handleRemoveMember(member.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          {members.length === 0 && (
            <p className="py-4 text-gray-500">No team members yet</p>
          )}
        </div>
      </div>
    </div>
  );
};