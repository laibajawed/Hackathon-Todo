/**
 * API client for making authenticated requests to the backend.
 * Handles JWT token attachment and error handling.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Make an authenticated API request.
 *
 * @param endpoint - API endpoint path (e.g., "/api/tasks")
 * @param options - Fetch options (method, headers, body, etc.)
 * @param token - Optional JWT token for authentication
 * @returns Parsed JSON response
 * @throws Error if request fails
 */
export async function apiClient<T = any>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Add Authorization header if token is provided
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: "include",
  });

  // Handle non-OK responses
  if (!response.ok) {
    let errorMessage = "API request failed";
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;

      // Handle expired JWT token - redirect to signin
      if (response.status === 401 && (
        errorMessage.includes("Token expired") ||
        errorMessage.includes("Invalid token") ||
        errorMessage.includes("Unauthorized")
      )) {
        // Clear stored auth data
        if (typeof window !== "undefined") {
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          // Redirect to signin page
          window.location.href = "/auth/signin";
        }
      }
    } catch {
      // If error response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  // Parse and return JSON response
  // Handle 204 No Content responses (e.g., DELETE operations)
  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return null as T;
  }

  return response.json();
}
