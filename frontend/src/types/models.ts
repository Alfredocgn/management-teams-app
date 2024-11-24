

export interface User {
  id:string;
  email:string;
  first_name:string;
  last_name:string;

}

export interface Project {
  id: string;
  title: string;
  description: string;
  tasks?: Task[];
}
export interface RegisterData {
  email:string;
  password:string;
  first_name:string;
  last_name:string
}

export interface LoginResponse {
  access_token:string;
  refresh_token:string;
  user:User;
}

export interface CreateProjectData {
  title:string;
  description:string;

}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  project_id: string;
  assignee_id?: string | null;
  due_date?: string | null;
  assignee?: User;
}

export interface CreateTaskData {
  title: string;
  description: string;
  due_date?: string | null;
  assignee_id?: string | null;
}

export interface ProjectUser {
  project_id: string;
  user_id: string;
  role: 'admin' | 'user';
  user?: User;
  project?: Project;
}

export interface CreateTaskFormProps {
  projectId: string;
  onSubmit: () => void;
  members: User[];
}