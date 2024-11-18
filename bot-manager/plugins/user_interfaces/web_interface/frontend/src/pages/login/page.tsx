import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../state/authStore";

export default function LoginPage(): JSX.Element {
  const { backendUrl, frontendPath } = useAuthStore();
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | undefined>();
  const navigate = useNavigate();

  const handleLogin = async (
    e: React.FormEvent<HTMLFormElement>,
  ): Promise<void> => {
    e.preventDefault();

    try {
      const response = await fetch(`${backendUrl}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      interface LoginResponse {
        success: boolean;
        error?: string;
      }
      const data: LoginResponse = (await response.json()) as LoginResponse;

      if (data.success) {
        navigate(`${frontendPath}/config`); // Redirect to config page on success
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={void handleLogin}>
        <div>
          <label>Password</label>
          <input
            type='password'
            value={password}
            onChange={(e): void => setPassword(e.target.value)}
            required
          />
        </div>
        <button type='submit'>Login</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
