import React, { useState } from "react";
import {matrixClient} from "matrix-react-library/"

export default function SignUp(): JSX.Element {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { registerResponse, registerMatrixUser } = matrixClient();

  const handleSignUp = (e: React.FormEvent): void => {
    e.preventDefault();
    try {
      registerMatrixUser(username, password);
      console.log("login success", registerResponse);
    } catch (error) {
      console.error("login failed", error);
      setError("Sign-up failed");
    }
  };

  return (
    <div>
      <h2>Sign Up</h2>
      <form onSubmit={(event) => event.preventDefault()}>
        <input
          type='text'
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder='Matrix username'
        />
        <input
          type='password'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder='Password'
        />
        <button type='submit'>Sign Up</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
