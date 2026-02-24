"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function HomePage() {
  const { user, loading, signup } = useAuth();
  const router = useRouter();

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  // Redirect authenticated users to tasks
  useEffect(() => {
    if (!loading && user) {
      router.push("/tasks");
    }
  }, [user, loading, router]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = "Last name is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Invalid email format";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await signup({ email: formData.email, password: formData.password });

      // Store display name in localStorage for frontend use
      localStorage.setItem(
        "userDisplayName",
        `${formData.firstName} ${formData.lastName}`
      );

      router.push("/tasks");
    } catch (err: any) {
      setErrors({ submit: err.message || "Failed to create account" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-deepBlack">
        <p className="text-white">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      {/* Left Section - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-warmOffWhite relative overflow-hidden">
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          {/* Logo */}
          <div>
            <h1 className="text-3xl font-bold text-deepBlack">MindSteps</h1>
          </div>

          {/* Main Content */}
          <div className="max-w-lg">
            <h2 className="text-4xl lg:text-5xl font-bold text-deepBlack leading-tight mb-6">
              Take the first step toward a more productive you.
            </h2>
            <p className="text-lg text-gray-700">
              Track your habits, stay focused, and achieve more every day
            </p>
          </div>

          {/* Footer space */}
          <div></div>
        </div>

        {/* Decorative Circles */}
        <div className="absolute top-20 right-20 w-64 h-64 bg-abstractCircle rounded-full opacity-60"></div>
        <div className="absolute bottom-32 right-40 w-48 h-48 bg-abstractCircle rounded-full opacity-60"></div>
        <div className="absolute top-1/2 right-10 w-32 h-32 bg-abstractCircle rounded-full opacity-60"></div>
      </div>

      {/* Right Section - Signup Form */}
      <div className="w-full lg:w-1/2 bg-deepBlack flex items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden mb-8">
            <h1 className="text-2xl font-bold text-white">MindSteps</h1>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">Create Account</h2>
            <p className="text-mutedPlaceholder">
              Start your journey to better productivity
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Submit Error */}
            {errors.submit && (
              <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-xl">
                <p className="text-sm text-red-400">{errors.submit}</p>
              </div>
            )}

            {/* First Name and Last Name */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <input
                  type="text"
                  name="firstName"
                  placeholder="First name"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-darkInput border border-borderGray rounded-xl text-white placeholder:text-mutedPlaceholder focus:outline-none focus:ring-2 focus:ring-beigeButton/50 transition-all"
                />
                {errors.firstName && (
                  <p className="text-sm text-red-400 mt-1">{errors.firstName}</p>
                )}
              </div>
              <div>
                <input
                  type="text"
                  name="lastName"
                  placeholder="Last name"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-darkInput border border-borderGray rounded-xl text-white placeholder:text-mutedPlaceholder focus:outline-none focus:ring-2 focus:ring-beigeButton/50 transition-all"
                />
                {errors.lastName && (
                  <p className="text-sm text-red-400 mt-1">{errors.lastName}</p>
                )}
              </div>
            </div>

            {/* Email */}
            <div>
              <input
                type="email"
                name="email"
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-darkInput border border-borderGray rounded-xl text-white placeholder:text-mutedPlaceholder focus:outline-none focus:ring-2 focus:ring-beigeButton/50 transition-all"
              />
              {errors.email && (
                <p className="text-sm text-red-400 mt-1">{errors.email}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <input
                type="password"
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-darkInput border border-borderGray rounded-xl text-white placeholder:text-mutedPlaceholder focus:outline-none focus:ring-2 focus:ring-beigeButton/50 transition-all"
              />
              {errors.password && (
                <p className="text-sm text-red-400 mt-1">{errors.password}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <input
                type="password"
                name="confirmPassword"
                placeholder="Confirm password"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-darkInput border border-borderGray rounded-xl text-white placeholder:text-mutedPlaceholder focus:outline-none focus:ring-2 focus:ring-beigeButton/50 transition-all"
              />
              {errors.confirmPassword && (
                <p className="text-sm text-red-400 mt-1">{errors.confirmPassword}</p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-beigeButton text-black font-semibold rounded-xl hover:bg-beigeButton/90 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Creating account..." : "Create Account"}
            </button>

            {/* Sign In Link */}
            <p className="text-center text-mutedPlaceholder text-sm">
              Already have an account?{" "}
              <a
                href="/auth/signin"
                className="text-beigeButton hover:text-beigeButton/80 transition-colors font-medium"
              >
                Sign in
              </a>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
