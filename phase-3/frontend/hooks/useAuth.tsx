/**
 * Authentication hook for managing user authentication state.
 * Provides user data, loading state, and authentication functions.
 */
"use client";

import { useState, useEffect, createContext, useContext, ReactNode } from "react";
import { User, AuthResponse, UserSignup, UserSignin } from "@/lib/types";
import { apiClient } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  signup: (data: UserSignup) => Promise<void>;
  signin: (data: UserSignin) => Promise<void>;
  signout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const signup = async (data: UserSignup) => {
    try {
      const response = await apiClient<AuthResponse>("/api/auth/signup", {
        method: "POST",
        body: JSON.stringify(data),
      });

      setUser(response.user);
      setToken(response.token);
      localStorage.setItem("token", response.token);
      localStorage.setItem("user", JSON.stringify(response.user));
    } catch (error) {
      throw error;
    }
  };

  const signin = async (data: UserSignin) => {
    try {
      const response = await apiClient<AuthResponse>("/api/auth/signin", {
        method: "POST",
        body: JSON.stringify(data),
      });

      setUser(response.user);
      setToken(response.token);
      localStorage.setItem("token", response.token);
      localStorage.setItem("user", JSON.stringify(response.user));
    } catch (error) {
      throw error;
    }
  };

  const signout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, signup, signin, signout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
