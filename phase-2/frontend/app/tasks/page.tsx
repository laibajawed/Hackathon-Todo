"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useTasks } from "@/hooks/useTasks";
import AuthGuard from "@/components/AuthGuard";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";
import { TaskCreate } from "@/lib/types";

export default function TasksPage() {
  const { user, signout } = useAuth();
  const { tasks, loading, error, createTask, updateTask, toggleTaskStatus, deleteTask } = useTasks();
  const router = useRouter();
  const [showForm, setShowForm] = useState(false);

  const handleSignout = () => {
    signout();
    router.push("/");
  };

  const handleCreateTask = async (taskData: TaskCreate) => {
    await createTask(taskData);
    setShowForm(false);
  };

  const handleUpdateTask = async (taskId: string, title: string, description: string) => {
    await updateTask(taskId, { title, description });
  };

  const handleToggleTask = async (taskId: string) => {
    await toggleTaskStatus(taskId);
  };

  const handleDeleteTask = async (taskId: string) => {
    await deleteTask(taskId);
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-4xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
                {user && (
                  <p className="text-sm text-gray-600 mt-1">
                    Signed in as {user.email}
                  </p>
                )}
              </div>
              <button
                onClick={handleSignout}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Sign Out
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          {/* Create Task Button/Form */}
          <div className="mb-6">
            {!showForm ? (
              <button
                onClick={() => setShowForm(true)}
                className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                + Create New Task
              </button>
            ) : (
              <div>
                <TaskForm onSubmit={handleCreateTask} />
                <button
                  onClick={() => setShowForm(false)}
                  className="mt-3 text-sm text-gray-600 hover:text-gray-900"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Task Statistics */}
          {!loading && tasks.length > 0 && (
            <div className="mb-6 grid grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Total Tasks</p>
                <p className="text-2xl font-bold text-gray-900">{tasks.length}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-green-600">
                  {tasks.filter((t) => t.status === "completed").length}
                </p>
              </div>
            </div>
          )}

          {/* Task List */}
          <TaskList
            tasks={tasks}
            loading={loading}
            onToggle={handleToggleTask}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask}
          />
        </main>
      </div>
    </AuthGuard>
  );
}
