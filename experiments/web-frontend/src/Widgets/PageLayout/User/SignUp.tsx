import React, { useState } from "react";

import { matrixClient } from "../../../context/MatrixClient";

export default function SignUp(): JSX.Element {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { registerResponse, registerMatrixUser } = matrixClient();

  return (
    <div>
      <h2>Sign Up</h2>
      <form onSubmit={(event): void => event.preventDefault()}>
        <input
          type='text'
          value={username}
          onChange={(e): void => setUsername(e.target.value)}
          placeholder='Matrix username'
        />
        <input
          type='password'
          value={password}
          onChange={(e): void => setPassword(e.target.value)}
          placeholder='Password'
        />
        <button
          onClick={(): void => void registerMatrixUser(username, password)}
          type='submit'
        >
          Sign Up
        </button>
      </form>
      {registerResponse && (
        <p style={{ color: "red" }}>{JSON.stringify(registerResponse)}</p>
      )}
    </div>
  );
}
