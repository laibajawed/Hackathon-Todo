"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useTasks } from "@/hooks/useTasks";
import AuthGuard from "@/components/AuthGuard";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";
import FloatingChatWidget from "@/components/FloatingChatWidget";
import { TaskCreate, TaskPriority } from "@/lib/types";

type StatusFilter = "all" | "active" | "done";
type PriorityFilter = "all" | "LOW" | "MEDIUM" | "HIGH";
type SortOption = "dateCreated" | "dateUpdated";

export default function TasksPage() {
  const { user, signout } = useAuth();
  const { tasks, loading, error, createTask, updateTask, toggleTaskStatus, deleteTask, fetchTasks } = useTasks();
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>("all");
  const [sortBy, setSortBy] = useState<SortOption>("dateCreated");

  const handleSignout = () => {
    signout();
    router.push("/");
  };

  const handleCreateTask = async (taskData: TaskCreate) => {
    await createTask(taskData);
    setShowForm(false);
  };

  const handleUpdateTask = async (taskId: string, title: string, description: string, priority: TaskPriority, tag: string) => {
    await updateTask(taskId, { title, description, priority, tag });
  };

  const handleToggleTask = async (taskId: string) => {
    await toggleTaskStatus(taskId);
  };

  const handleDeleteTask = async (taskId: string) => {
    await deleteTask(taskId);
  };

  // Filter and sort tasks
  const filteredAndSortedTasks = useMemo(() => {
    let filtered = [...tasks];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (task) =>
          task.title.toLowerCase().includes(query) ||
          (task.description?.toLowerCase().includes(query) ?? false)
      );
    }

    // Apply status filter
    if (statusFilter === "active") {
      filtered = filtered.filter((task) => task.status === "pending");
    } else if (statusFilter === "done") {
      filtered = filtered.filter((task) => task.status === "completed");
    }

    // Apply priority filter
    if (priorityFilter !== "all") {
      filtered = filtered.filter((task) => task.priority === priorityFilter);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      if (sortBy === "dateCreated") {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      } else if (sortBy === "dateUpdated") {
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      }
      return 0;
    });

    return filtered;
  }, [tasks, searchQuery, statusFilter, priorityFilter, sortBy]);

  return (
    <AuthGuard>
      <div className="min-h-screen bg-warmOffWhite">
        {/* Header Navigation */}
        <header className="bg-beigeButton shadow-sm border-b border-abstractCircle">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-8">
                <h1 className="text-xl font-bold text-deepBlack">MindSteps</h1>
              </div>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setShowForm(true)}
                  className="px-4 py-2 text-sm font-semibold text-white bg-deepBlack rounded-xl hover:bg-deepBlack/90 focus:outline-none focus:ring-2 focus:ring-deepBlack/50 transition-colors"
                >
                  + New Task
                </button>
                {user && (
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-deepBlack">{user.email}</span>
                    <button
                      onClick={handleSignout}
                      className="px-3 py-2 text-sm font-medium text-white bg-deepBlack rounded-xl hover:bg-deepBlack/90 focus:outline-none focus:ring-2 focus:ring-deepBlack/50 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          {/* Task Form Modal */}
          {showForm && (
            <div className="fixed inset-0 bg-deepBlack bg-opacity-80 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
                <h2 className="text-xl font-semibold text-deepBlack mb-4">Create New Task</h2>
                <TaskForm onSubmit={handleCreateTask} onCancel={() => setShowForm(false)} />
              </div>
            </div>
          )}

          {/* Page Title */}
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-deepBlack">Your Tasks</h2>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-white border border-abstractCircle rounded-xl focus:outline-none focus:ring-2 focus:ring-beigeButton/50 text-deepBlack placeholder-mutedPlaceholder transition-all"
            />
          </div>

          {/* Filters and Sort */}
          <div className="mb-6 flex flex-wrap gap-6 items-center">
            {/* Status Filter */}
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-deepBlack uppercase tracking-wide">Status</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setStatusFilter("all")}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
                    statusFilter === "all"
                      ? "bg-beigeButton text-deepBlack"
                      : "bg-white text-deepBlack border border-abstractCircle hover:bg-abstractCircle/30"
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setStatusFilter("active")}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
                    statusFilter === "active"
                      ? "bg-beigeButton text-deepBlack"
                      : "bg-white text-deepBlack border border-abstractCircle hover:bg-abstractCircle/30"
                  }`}
                >
                  Active
                </button>
                <button
                  onClick={() => setStatusFilter("done")}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
                    statusFilter === "done"
                      ? "bg-beigeButton text-deepBlack"
                      : "bg-white text-deepBlack border border-abstractCircle hover:bg-abstractCircle/30"
                  }`}
                >
                  Done
                </button>
              </div>
            </div>

            {/* Priority Filter */}
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-deepBlack uppercase tracking-wide">Priority</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPriorityFilter("all")}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
                    priorityFilter === "all"
                      ? "bg-beigeButton text-deepBlack"
                      : "bg-white text-deepBlack border border-abstractCircle hover:bg-abstractCircle/30"
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setPriorityFilter("LOW")}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
                    priorityFilter === "LOW"
                      ? "bg-beigeButton text-deepBlack"
                      : "bg-white text-deepBlack border border-abstractCircle hover:bg-abstractCircle/30"
                  }`}
                >
                  Low
                </button>
                <button
                  onClick={() => setPriorityFilter("MEDIUM")}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
                    priorityFilter === "MEDIUM"
                      ? "bg-beigeButton text-deepBlack"
                      : "bg-white text-deepBlack border border-abstractCircle hover:bg-abstractCircle/30"
                  }`}
                >
                  Medium
                </button>
                <button
                  onClick={() => setPriorityFilter("HIGH")}
                  className={`px-4 py-2 text-sm font-medium rounded-xl transition-colors ${
                    priorityFilter === "HIGH"
                      ? "bg-beigeButton text-deepBlack"
                      : "bg-white text-deepBlack border border-abstractCircle hover:bg-abstractCircle/30"
                  }`}
                >
                  High
                </button>
              </div>
            </div>

            {/* Sort Dropdown */}
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-deepBlack uppercase tracking-wide">Sort</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="px-4 py-2 text-sm font-medium bg-white text-deepBlack border border-abstractCircle rounded-xl hover:bg-abstractCircle/30 focus:outline-none focus:ring-2 focus:ring-beigeButton/50 transition-all"
              >
                <option value="dateCreated">Date Created</option>
                <option value="dateUpdated">Date Updated</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Task List */}
          <TaskList
            tasks={filteredAndSortedTasks}
            loading={loading}
            onToggle={handleToggleTask}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask}
            onCreateTask={() => setShowForm(true)}
          />
        </main>
      </div>
      <FloatingChatWidget onTasksChanged={fetchTasks} />
    </AuthGuard>
  );
}
