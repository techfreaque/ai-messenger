import React, { useState } from "react";

import { matrixClient } from "../../../context/MatrixClient";

export default function Login(): JSX.Element {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { loginToMatrix, loginResponse } = matrixClient();
  return (
    <div>
      <h2>Sign Up</h2>
      <form onSubmit={(event): void => event.preventDefault()}>
        <input
          type='text'
          name='email'
          value={username}
          onChange={(e): void => setUsername(e.target.value)}
          placeholder='Matrix username'
        />
        <input
          type='password'
          name='password'
          value={password}
          onChange={(e): void => setPassword(e.target.value)}
          placeholder='Password'
        />
        <button
          onClick={(): void => void loginToMatrix(username, password)}
          type='submit'
        >
          Log in
        </button>
      </form>
      {loginResponse && (
        <p style={{ color: "red" }}>{JSON.stringify(loginResponse)}</p>
      )}
    </div>
  );
}
