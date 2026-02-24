/**
 * TaskItem component for displaying an individual task.
 * Shows task title, description, priority, tag, status indicator, and action buttons.
 */
"use client";

import { Task, TaskStatus, TaskPriority } from "@/lib/types";
import { useState } from "react";

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: string) => Promise<void>;
  onUpdate: (taskId: string, title: string, description: string, priority: TaskPriority, tag: string) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export default function TaskItem({ task, onToggle, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");
  const [editPriority, setEditPriority] = useState<TaskPriority>(task.priority || TaskPriority.MEDIUM);
  const [editTag, setEditTag] = useState(task.tag || "");
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
      await onUpdate(task.id, editTitle, editDescription, editPriority, editTag);
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
    setEditPriority(task.priority || TaskPriority.MEDIUM);
    setEditTag(task.tag || "");
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
      <div className="bg-white p-4 rounded-xl shadow-sm border border-abstractCircle">
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value.slice(0, 200))}
            className="w-full px-3 py-2 border border-abstractCircle rounded-xl focus:outline-none focus:ring-2 focus:ring-beigeButton/50 text-deepBlack bg-white"
            placeholder="Task title"
            disabled={loading}
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value.slice(0, 1000))}
            className="w-full px-3 py-2 border border-abstractCircle rounded-xl focus:outline-none focus:ring-2 focus:ring-beigeButton/50 text-deepBlack bg-white"
            placeholder="Task description (optional)"
            rows={3}
            disabled={loading}
          />

          {/* Priority selector */}
          <div>
            <label className="block text-xs font-medium text-deepBlack mb-1">Priority</label>
            <div className="flex gap-2">
              {[TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH].map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setEditPriority(level)}
                  disabled={loading}
                  className={`flex-1 px-3 py-1.5 text-sm rounded-xl font-medium transition-all disabled:opacity-50 ${
                    editPriority === level
                      ? 'bg-beigeButton text-deepBlack shadow-sm'
                      : 'bg-abstractCircle text-deepBlack/70 hover:bg-abstractCircle/80'
                  }`}
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Tag field */}
          <input
            type="text"
            value={editTag}
            onChange={(e) => setEditTag(e.target.value.slice(0, 50))}
            className="w-full px-3 py-2 border border-abstractCircle rounded-xl focus:outline-none focus:ring-2 focus:ring-beigeButton/50 text-deepBlack bg-white"
            placeholder="Tag (optional)"
            disabled={loading}
          />

          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-4 py-2 bg-beigeButton text-deepBlack font-semibold rounded-xl hover:bg-beigeButton/90 disabled:opacity-50 transition-colors"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              disabled={loading}
              className="px-4 py-2 bg-abstractCircle text-deepBlack rounded-xl hover:bg-abstractCircle/80 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-abstractCircle hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={isCompleted}
          onChange={handleToggle}
          disabled={loading}
          className="mt-1 h-5 w-5 text-beigeButton rounded focus:ring-beigeButton/50 cursor-pointer"
        />
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-medium ${
              isCompleted ? "line-through text-mutedPlaceholder" : "text-deepBlack"
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`mt-1 text-sm ${
                isCompleted ? "line-through text-mutedPlaceholder" : "text-gray-700"
              }`}
            >
              {task.description}
            </p>
          )}
          <div className="mt-2 flex items-center gap-2 text-xs flex-wrap">
            <span
              className={`px-2 py-1 rounded-full ${
                isCompleted
                  ? "bg-green-100 text-green-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {isCompleted ? "Completed" : "Pending"}
            </span>
            {task.priority && (
              <span
                className={`px-2 py-1 rounded-full ${
                  task.priority === TaskPriority.HIGH
                    ? "bg-red-100 text-red-800"
                    : task.priority === TaskPriority.MEDIUM
                    ? "bg-orange-100 text-orange-800"
                    : "bg-blue-100 text-blue-800"
                }`}
              >
                {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
              </span>
            )}
            {task.tag && (
              <span className="px-2 py-1 rounded-full bg-purple-100 text-purple-800">
                {task.tag}
              </span>
            )}
            <span className="text-mutedPlaceholder">
              Created: {new Date(task.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            disabled={loading}
            className="px-3 py-1 text-sm text-deepBlack hover:bg-abstractCircle rounded-xl disabled:opacity-50 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={loading}
            className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded-xl disabled:opacity-50 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
