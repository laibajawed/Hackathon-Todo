/**
 * TaskForm component for creating new tasks.
 * Provides input fields for title, description, priority, and tag.
 */
"use client";

import { useState } from "react";
import { TaskCreate, TaskPriority } from "@/lib/types";

interface TaskFormProps {
  onSubmit: (taskData: TaskCreate) => Promise<void>;
  onCancel: () => void;
}

export default function TaskForm({ onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>(TaskPriority.MEDIUM);
  const [tag, setTag] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError("Title cannot be empty");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        priority: priority,
        tag: tag.trim() || undefined,
      });

      // Clear form on success
      setTitle("");
      setDescription("");
      setPriority(TaskPriority.MEDIUM);
      setTag("");
    } catch (err: any) {
      setError(err.message || "Failed to create task");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Title field with character counter */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <label htmlFor="title" className="text-sm font-medium text-deepBlack">
            Title <span className="text-red-500">*</span>
          </label>
          <span className="text-xs text-mutedPlaceholder">
            {title.length}/200
          </span>
        </div>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value.slice(0, 200))}
          placeholder="Enter task title"
          required
          disabled={loading}
          className="w-full px-4 py-3 border border-abstractCircle rounded-xl focus:outline-none focus:ring-2 focus:ring-beigeButton/50 disabled:opacity-50 text-deepBlack bg-white placeholder-mutedPlaceholder transition-all"
        />
      </div>

      {/* Description field with character counter */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <label htmlFor="description" className="text-sm font-medium text-deepBlack">
            Description (optional)
          </label>
          <span className="text-xs text-mutedPlaceholder">
            {description.length}/1000
          </span>
        </div>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value.slice(0, 1000))}
          placeholder="Enter task description"
          rows={3}
          disabled={loading}
          className="w-full px-4 py-3 border border-abstractCircle rounded-xl focus:outline-none focus:ring-2 focus:ring-beigeButton/50 disabled:opacity-50 text-deepBlack bg-white placeholder-mutedPlaceholder transition-all"
        />
      </div>

      {/* Priority selector */}
      <div>
        <label className="block text-sm font-medium text-deepBlack mb-2">
          Priority
        </label>
        <div className="flex gap-2">
          {[TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH].map((level) => (
            <button
              key={level}
              type="button"
              onClick={() => setPriority(level)}
              disabled={loading}
              className={`flex-1 px-4 py-2 rounded-xl font-medium transition-all disabled:opacity-50 ${
                priority === level
                  ? 'bg-beigeButton text-deepBlack shadow-sm'
                  : 'bg-abstractCircle text-deepBlack/70 hover:bg-abstractCircle/80'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Tag field with character counter */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <label htmlFor="tag" className="text-sm font-medium text-deepBlack">
            Tag (optional)
          </label>
          <span className="text-xs text-mutedPlaceholder">
            {tag.length}/50
          </span>
        </div>
        <input
          id="tag"
          type="text"
          value={tag}
          onChange={(e) => setTag(e.target.value.slice(0, 50))}
          placeholder="e.g., work, personal"
          disabled={loading}
          className="w-full px-4 py-3 border border-abstractCircle rounded-xl focus:outline-none focus:ring-2 focus:ring-beigeButton/50 disabled:opacity-50 text-deepBlack bg-white placeholder-mutedPlaceholder transition-all"
        />
      </div>

      {/* Error display */}
      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-xl">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="flex-1 px-4 py-3 bg-abstractCircle text-deepBlack font-semibold rounded-xl hover:bg-abstractCircle/80 disabled:opacity-50 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="flex-1 px-4 py-3 bg-beigeButton text-deepBlack font-semibold rounded-xl hover:bg-beigeButton/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Creating...' : 'Create Task'}
        </button>
      </div>
    </form>
  );
}
