/**
 * TaskItem component for displaying an individual task.
 * Shows task title, description, status indicator, and action buttons.
 */
"use client";

import { Task, TaskStatus } from "@/lib/types";
import { useState } from "react";

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: string) => Promise<void>;
  onUpdate: (taskId: string, title: string, description: string) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export default function TaskItem({ task, onToggle, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");
  const [loading, setLoading] = useState(false);

  const isCompleted = task.status === TaskStatus.COMPLETED;

  const handleToggle = async () => {
    setLoading(true);
    try {
      await onToggle(task.id);
    } catch (error) {
      console.error("Failed to toggle task:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!editTitle.trim()) {
      alert("Title cannot be empty");
      return;
    }

    setLoading(true);
    try {
      await onUpdate(task.id, editTitle, editDescription);
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to update task:", error);
      alert("Failed to update task");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) {
      return;
    }

    setLoading(true);
    try {
      await onDelete(task.id);
    } catch (error) {
      console.error("Failed to delete task:", error);
      alert("Failed to delete task");
    } finally {
      setLoading(false);
    }
  };

  if (isEditing) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
            placeholder="Task title"
            disabled={loading}
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
            placeholder="Task description (optional)"
            rows={3}
            disabled={loading}
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              disabled={loading}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={isCompleted}
          onChange={handleToggle}
          disabled={loading}
          className="mt-1 h-5 w-5 text-blue-600 rounded focus:ring-blue-500 cursor-pointer"
        />
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-medium ${
              isCompleted ? "line-through text-gray-500" : "text-gray-900"
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`mt-1 text-sm ${
                isCompleted ? "line-through text-gray-400" : "text-gray-600"
              }`}
            >
              {task.description}
            </p>
          )}
          <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
            <span
              className={`px-2 py-1 rounded-full ${
                isCompleted
                  ? "bg-green-100 text-green-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {isCompleted ? "Completed" : "Pending"}
            </span>
            <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            disabled={loading}
            className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-md disabled:opacity-50"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={loading}
            className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-md disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
