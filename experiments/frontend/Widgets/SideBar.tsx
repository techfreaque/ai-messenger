import { useState } from "react";

import { matrixClient } from "@/context/MatrixClient";
import Login from "@/Widgets/Login";

import RoomList from "./RoomList";
import SignUp from "./SignUp";

export default function Sidebar(): JSX.Element {
  const [isSignUp, setIsSignUp] = useState(false);
  const { client, } = matrixClient();
  console.log("client?.isLoggedIn()", client?.isLoggedIn());
  if (!client?.isLoggedIn()) {
    return (
      <div>
        {isSignUp ? <SignUp /> : <Login />}
        <button onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp
            ? "Already have an account? Log in"
            : "Don't have an account? Sign up"}
        </button>
        {/* <button onClick={init}>init</button> */}
      </div>
    );
  }

  return (
    <div>
      <RoomList />
      {/* <button onClick={() => initRooms()}>reload Rooms</button> */}
      {/* <button onClick={() => setSelectedRoom("!someRoomId:matrix.org")}>
          Go to Room
        </button> */}
    </div>
  );
}
