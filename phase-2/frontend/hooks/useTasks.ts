/**
 * Custom hook for managing tasks data and operations.
 * Provides functions for fetching, creating, updating, and deleting tasks.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { Task, TaskCreate, TaskUpdate, TaskStatus } from "@/lib/types";
import { apiClient } from "@/lib/api";
import { useAuth } from "./useAuth";

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  const fetchTasks = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await apiClient<Task[]>("/api/tasks", {}, token);
      setTasks(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch tasks");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = async (taskData: TaskCreate): Promise<Task> => {
    if (!token) throw new Error("Not authenticated");

    try {
      const newTask = await apiClient<Task>(
        "/api/tasks",
        {
          method: "POST",
          body: JSON.stringify(taskData),
        },
        token
      );

      // Optimistic update
      setTasks((prev) => [newTask, ...prev]);
      return newTask;
    } catch (err: any) {
      throw new Error(err.message || "Failed to create task");
    }
  };

  const updateTask = async (taskId: string, taskData: TaskUpdate): Promise<Task> => {
    if (!token) throw new Error("Not authenticated");

    try {
      const updatedTask = await apiClient<Task>(
        `/api/tasks/${taskId}`,
        {
          method: "PUT",
          body: JSON.stringify(taskData),
        },
        token
      );

      // Update local state
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      return updatedTask;
    } catch (err: any) {
      throw new Error(err.message || "Failed to update task");
    }
  };

  const toggleTaskStatus = async (taskId: string): Promise<Task> => {
    if (!token) throw new Error("Not authenticated");

    try {
      const updatedTask = await apiClient<Task>(
        `/api/tasks/${taskId}/toggle`,
        {
          method: "PATCH",
        },
        token
      );

      // Update local state
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      return updatedTask;
    } catch (err: any) {
      throw new Error(err.message || "Failed to toggle task status");
    }
  };

  const deleteTask = async (taskId: string): Promise<void> => {
    if (!token) throw new Error("Not authenticated");

    try {
      await apiClient(
        `/api/tasks/${taskId}`,
        {
          method: "DELETE",
        },
        token
      );

      // Remove from local state
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err: any) {
      throw new Error(err.message || "Failed to delete task");
    }
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    toggleTaskStatus,
    deleteTask,
  };
}
