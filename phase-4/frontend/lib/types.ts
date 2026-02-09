/**
 * TypeScript type definitions for the Todo application.
 * Defines interfaces for User, Task, and API responses.
 */

/**
 * Task completion status enum.
 */
export enum TaskStatus {
  PENDING = "pending",
  COMPLETED = "completed",
}

/**
 * User entity.
 */
export interface User {
  id: string;
  email: string;
  created_at: string;
}

/**
 * Task entity.
 */
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

/**
 * Authentication response from signup/signin endpoints.
 */
export interface AuthResponse {
  user: User;
  token: string;
}

/**
 * User signup request payload.
 */
export interface UserSignup {
  email: string;
  password: string;
}

/**
 * User signin request payload.
 */
export interface UserSignin {
  email: string;
  password: string;
}

/**
 * Task creation request payload.
 */
export interface TaskCreate {
  title: string;
  description?: string;
}

/**
 * Task update request payload.
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
}

/**
 * API error response.
 */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}
