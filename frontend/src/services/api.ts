/* eslint-disable no-useless-catch */
import axios from "axios";
import {
  CreateProjectData,
  CreateTaskData,
  LoginResponse,
  Project,
  RegisterData,
  Task,
} from "../types/models";

const api = axios.create({
  baseURL: `http://44.204.12.162`,
  headers: {
    "Content-Type": "application/json",
  },
});

export const authApi = {
  register: async (data: RegisterData) => {
    try {
      const response = await api.post("/register", data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  login: async (email: string, password: string): Promise<LoginResponse> => {
    const data = {
      username: email,
      password: password,
      grant_type: "password",
    };

    const response = await api.post("/login", data, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return response.data;
  },
};

export const projectApi = {
  getProjects: async () => {
    try {
      const response = await api.get("/api/projects");
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  createProject: async (data: CreateProjectData) => {
    try {
      const response = await api.post("/api/projects", data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getProject: async (id: string) => {
    try {
      const response = await api.get(`/api/projects/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateProject: async (id: string, data: Partial<Project>) => {
    try {
      const response = await api.put(`/api/projects/${id}`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  deleteProject: async (id: string) => {
    try {
      const response = await api.delete(`/api/projects/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const taskApi = {
  getTasks: async (projectId: string) => {
    try {
      const response = await api.get(`/api/projects/${projectId}/tasks`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  createTask: async (projectId: string, data: CreateTaskData) => {
    try {
      const response = await api.post(`/api/projects/${projectId}/tasks`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  updateTask: async (
    projectId: string,
    taskId: string,
    data: Partial<Task>
  ) => {
    try {
      const response = await api.put(
        `/api/projects/${projectId}/tasks/${taskId}`,
        data
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  deleteTask: async (projectId: string, taskId: string) => {
    try {
      const response = await api.delete(
        `/api/projects/${projectId}/tasks/${taskId}`
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const projectMemberApi = {
  getProjectMembers: async (projectId: string) => {
    try {
      const response = await api.get(`/api/projects/${projectId}/members`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  addProjectMember: async (projectId: string, userId: string) => {
    try {
      const response = await api.post(
        `/api/projects/${projectId}/members/${userId}`
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  removeProjectMember: async (projectId: string, userId: string) => {
    try {
      const response = await api.delete(
        `/api/projects/${projectId}/members/${userId}`
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const userApi = {
  searchByEmail: async (email: string) => {
    try {
      const response = await api.get(`/api/users/search?email=${email}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  getSubscriptionStatus: async () => {
    try {
      const response = await api.get("/api/subscription-status");
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const subscriptionApi = {
  getProducts: async () => {
    const response = await api.get("/api/products");
    return response.data;
  },

  createCheckoutSession: async (price_id: string) => {
    const response = await api.post("/api/create-checkout-session", {
      price_id,
    });
    return response.data;
  },
};
