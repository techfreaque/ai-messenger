import { useState } from "react";
import type { MatrixRoom } from "../state/MatrixClient";
import { useMatrixClient } from "../state/MatrixClient";

export default function MessageRoom(): JSX.Element {
  const [infoMessage, setInfoMessage] = useState("");
  const { selectedRoom, rooms, sendMessage } = useMatrixClient();

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
  console.log("current room", room);
  return (
    <div className='p-6 z-0'>
      <h3>Room: {selectedRoom}</h3>
      <div className='messages'>
        {roomMessages?.length ? (
          roomMessages.map((msg, index) => (
            <div key={index}>
              ree
              <strong>{JSON.stringify(msg.events)}:</strong>
            </div>
          ))
        ) : (
          <div>No Messages yet</div>
        )}
      </div>
      <div style={{ position: "fixed", bottom: "0" }}>
        <input
          type='text'
          value={infoMessage}
          onChange={(e): void => setInfoMessage(e.target.value)}
          placeholder='Type your message'
        />
        <button onClick={void handleSendMessage}>Send</button>
      </div>
    </div>
  );
}
