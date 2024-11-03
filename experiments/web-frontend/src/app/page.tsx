"use client";

import React, { useState } from "react";

import { matrixClient } from "../context/MatrixClient";
import MessageRoom from "../Widgets/MessagingComponent";
import Login from "../Widgets/PageLayout/User/Login";
import SignUp from "../Widgets/PageLayout/User/SignUp";

export default function Home(): JSX.Element {
  const { selectedRoom, client } = matrixClient();
  const [isSignUp, setIsSignUp] = useState(false);
  if (!client?.isLoggedIn()) {
    return (
      <div>
        {isSignUp ? <SignUp /> : <Login />}
        <button onClick={(): void => setIsSignUp(!isSignUp)}>
          {isSignUp
            ? "Already have an account? Log in"
            : "Don't have an account? Sign up"}
        </button>
        {/* <button onClick={init}>init</button> */}
      </div>
    );
  }

  return selectedRoom ? (
    <MessageRoom />
  ) : (
    <div>Select or create a new chat</div>
  );
}
