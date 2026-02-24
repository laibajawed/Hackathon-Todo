/**
 * TaskList component for displaying a list of tasks.
 * Handles empty state and renders TaskItem components.
 */
"use client";

import { Task, TaskPriority } from "@/lib/types";
import TaskItem from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  onToggle: (taskId: string) => Promise<void>;
  onUpdate: (taskId: string, title: string, description: string, priority: TaskPriority, tag: string) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
  onCreateTask?: () => void;
}

export default function TaskList({ tasks, loading, onToggle, onUpdate, onDelete, onCreateTask }: TaskListProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-beigeButton"></div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4">
        <p className="text-center text-gray-700 text-lg mb-6 max-w-md">
          No tasks yet. Create your first task to get started on your productivity journey.
        </p>
        {onCreateTask && (
          <button
            onClick={onCreateTask}
            className="px-6 py-3 bg-beigeButton text-deepBlack font-semibold rounded-xl hover:bg-beigeButton/90 focus:outline-none focus:ring-2 focus:ring-beigeButton/50 transition-colors"
          >
            + Create Task
          </button>
        )}
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
