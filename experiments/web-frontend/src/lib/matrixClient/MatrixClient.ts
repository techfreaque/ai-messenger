"use client";

import type {
  AuthType,
  EventType,
  ICreateClientOpts,
  ISendEventResponse,
  LoginResponse,
  MatrixClient,
  MsgType,
  RegisterResponse,
  Room,
  RoomState,
  RoomStateEvent,
} from "matrix-js-sdk";

import type { LocalStorage } from "../../context/MatrixClient";

let sdk:
  | {
      AuthType: typeof AuthType;
      RoomStateEvent: typeof RoomStateEvent;
      EventType: typeof EventType;
      MsgType: typeof MsgType;
    }
  | undefined = undefined;

export async function initializeClient(
  baseUrl: string,
  loginData: LocalStorage | undefined,
): Promise<MatrixClient> {
  const clientProps: ICreateClientOpts = {
    baseUrl,
  };
  if (loginData?.access_token && loginData?.user_id) {
    clientProps.accessToken = loginData.access_token;
    clientProps.userId = loginData.user_id;
  }
  const { createClient, AuthType, RoomStateEvent, EventType, MsgType } =
    await import("matrix-js-sdk");
  sdk = { AuthType, RoomStateEvent, EventType, MsgType };
  return createClient(clientProps);
}

export const registerMatrixUser = async (
  client: MatrixClient,
  username: string,
  password: string,
): Promise<RegisterResponse> => {
  if (!client || !sdk) {
    throw new Error("Matrix client is not initialized!");
  }

  const registerResponse = await client.registerRequest({
    username,
    password,
    auth: {
      // type: "m.login.dummy",
      type: sdk.AuthType.Password,
    },
  });

  await client.startClient();
  return registerResponse;
};

export const loginToMatrix = async (
  client: MatrixClient,
  username: string,
  password: string,
): Promise<LoginResponse> => {
  if (!client) {
    throw new Error("Matrix client is not initialized!");
  }

  const response = await client.login("m.login.password", {
    user: username,
    password,
  });
  await client.startClient({ lazyLoadMembers: true });
  return response;
};

export function initMessageListener(
  client: MatrixClient,
  onNewMessage: (state: RoomState) => void,
): void {
  if (!client || !sdk) {
    throw new Error("Matrix client is not initialized!");
  }
  client.on(sdk.RoomStateEvent.Update, (roomState: RoomState) => {
    console.log("new roomState", roomState);
    onNewMessage(roomState);
  });
}

export const getRooms = (client: MatrixClient): Room[] => {
  if (!client) {
    throw new Error("Matrix client is not initialized!");
  }
  return client.getRooms();
};

export const sendMessage = async (
  client: MatrixClient,
  roomId: string,
  message: string,
): Promise<ISendEventResponse> => {
  if (!client || !sdk) {
    throw new Error("Matrix client is not initialized!");
  }

  try {
    const response = await client.sendEvent(roomId, sdk.EventType.RoomMessage, {
      msgtype: sdk.MsgType.Text,
      body: message,
    });
    return response;
  } catch (error) {
    console.error("Failed to send message:", error);
    throw error;
  }
};

// event example
// const client = create<clientType>((set) => ({
//   sendCustomEvent: async (eventType: string, content: object) => {
//     set((state) => {
//       const client = state.client;
//       if (client) {
//         const roomId = "!your_room_id_here"; // Replace with your target room ID

//         // Send a custom event to the specified room
//         client
//           .sendEvent(roomId, eventType, content)
//           .then(() => {
//             console.log("Event sent successfully");
//           })
//           .catch((err) => {
//             console.error("Failed to send event:", err);
//           });
//       }
//     });
//   },
//   fetchCustomEvents: async () => {
//     set((state) => {
//       const client = state.client;
//       if (client) {
//         const roomId = "!your_room_id_here"; // Replace with your target room ID

//         // Fetch the state of the room
//         return client
//           .getRoom(roomId)
//           ?.getStateEvents("com.example.theme", "")
//           .then((event) => {
//             return event?.getContent();
//           })
//           .catch((err) => {
//             console.error("Failed to fetch events:", err);
//             return null;
//           });
//       }
//     });
//   },
// }));
