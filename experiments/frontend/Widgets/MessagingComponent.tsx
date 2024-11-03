import React, { useState } from "react";

import type { MatrixRoom } from "@/context/MatrixClient";
import { matrixClient } from "@/context/MatrixClient";

export default function MessageRoom(): JSX.Element {
  const [infoMessage, setInfoMessage] = useState("");
  const { selectedRoom, rooms, sendMessage } = matrixClient();

  if (!selectedRoom) {
    return <></>;
  }

  const room: undefined | MatrixRoom = selectedRoom
    ? rooms[selectedRoom]
    : undefined;
  const roomMessages = room?.messages;
  const handleSendMessage = async (): Promise<void> => {
    await sendMessage(selectedRoom, infoMessage);
    setInfoMessage("");
  };

  return (
    <div>
      <div>
        <h3>Room: {selectedRoom}</h3>
        <div className='messages'>
          {roomMessages?.map((msg, index) => (
            <div key={index}>
              <strong>{msg.roomId}:</strong>
            </div>
          ))}
        </div>
        <div style={{ position: "fixed", bottom: "0" }}>
          <input
            type='text'
            value={infoMessage}
            onChange={(e) => setInfoMessage(e.target.value)}
            placeholder='Type your message'
          />
          <button onClick={void handleSendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}
