/**
 * TaskList component for displaying a list of tasks.
 * Handles empty state and renders TaskItem components.
 */
"use client";

import { Task } from "@/lib/types";
import TaskItem from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  onToggle: (taskId: string) => Promise<void>;
  onUpdate: (taskId: string, title: string, description: string) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export default function TaskList({ tasks, loading, onToggle, onUpdate, onDelete }: TaskListProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📝</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No tasks yet</h3>
        <p className="text-gray-600">Create your first task to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
