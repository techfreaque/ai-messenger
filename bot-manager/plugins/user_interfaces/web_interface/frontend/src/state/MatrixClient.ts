import type {
  LoginResponse,
  MatrixClient,
  MatrixEvent,
  RegisterResponse,
  Room,
  RoomState,
} from "matrix-js-sdk";
import { create } from "zustand";

import {
  getRooms,
  initializeClient,
  initMessageListener,
  loginToMatrix,
  registerMatrixUser,
  sendMessage,
} from "../lib/matrixClient/MatrixClient";

export interface MatrixClientContextType {
  client: MatrixClient | undefined;
  server: string;
  rooms: { [roomId: string]: MatrixRoom };

  init: () => Promise<void>;
  registerMatrixUser: (username: string, password: string) => Promise<void>;
  registerResponse: RegisterResponse | undefined;
  loginToMatrix: (username: string, password: string) => Promise<void>;
  loginResponse: LoginResponse | undefined;
  selectedRoom: string | undefined;
  setSelectedRoom: (roomId: string | undefined) => void;
  onNewMessage: (roomState: RoomState) => void;
  initRoom: (roomId: string) => void;
  sendMessage: (roomId: string, message: string) => Promise<void>;
}

export interface MatrixRoom {
  roomId: string;
  info: MatrixEvent[];
  roomState: RoomState | undefined;
  messages: RoomState[];
  infoOther?: Room;
}

export const useMatrixClient = create<MatrixClientContextType>((set, get) => ({
  client: undefined,
  server: "https://matrix.org",
  rooms: {},

  selectedRoom: undefined,
  setSelectedRoom: (roomId): void => {
    set((state) => {
      if (roomId) {
        localStorage.setItem("selectedRoom", roomId);
      } else {
        localStorage.removeItem("selectedRoom");
      }
      return { ...state, selectedRoom: roomId };
    });
  },

  init: async (): Promise<void> => {
    const currentState = get();
    if (currentState.client) {
      console.error("Should not initialize twice");
      return;
    }
    window.global = window; //
    const login = localStorage.getItem("login");
    const selectedRoom = localStorage.getItem("selectedRoom") || undefined;
    const loginData: LocalStorage | undefined = login
      ? (JSON.parse(login) as LocalStorage)
      : undefined;
    const client = await initializeClient(get().server, loginData);
    let newData: MatrixClientContextType | undefined = undefined;
    if (loginData?.access_token && loginData?.user_id) {
      newData = await _start(client, currentState);
    }
    console.log("rooms", newData?.rooms);
    set((state) => {
      return {
        ...(newData || state),
        client,
        loginResponse: loginData,
        selectedRoom,
      };
    });
  },

  onNewMessage: (roomState: RoomState): void => {
    set((state) => {
      const newState = { ...state };
      const room = newState.rooms[roomState.roomId];
      if (room) {
        room.roomState = roomState;
        room.messages = [...room.messages, roomState];
      } else {
        throw new Error("Room not initialized yet");
        // newState.rooms[roomState.roomId] = {
        //   roomId: roomState.roomId,
        //   roomState,
        //   messages: [roomState],
        //   info: [],
        // };
      }
      return newState;
    });
  },

  registerResponse: undefined,
  registerMatrixUser: async (username, password): Promise<void> => {
    const state = get();
    if (!state.client) {
      throw new Error("Matrix client is not initialized!");
    }
    const response = await registerMatrixUser(state.client, username, password);
    set((state) => {
      return {
        ...state,
        registerResponse: response,
      };
    });
  },

  loginResponse: undefined,
  loginToMatrix: async (username, password): Promise<void> => {
    const currentState = get();
    if (!currentState.client) {
      throw new Error("Matrix client is not initialized!");
    }
    const loginData = await loginToMatrix(
      currentState.client,
      username,
      password,
    ); // Your registration function
    localStorage.setItem("login", JSON.stringify(loginData));
    let newState: undefined | MatrixClientContextType = undefined;
    if (loginData?.access_token && loginData?.user_id) {
      newState = await _start(currentState.client, currentState);
    }
    set((state) => {
      return {
        ...(newState || state),
        client: currentState.client,
        registerResponse: loginData,
      };
    });
  },

  initRoom: (roomId): void =>
    set((state) => {
      const newState = { ...state };
      if (!state.client) {
        throw new Error("Matrix client is not initialized!");
      }

      const matrixRoom = state.client.getRoom(roomId);
      if (!matrixRoom) {
        console.error(`Room with id ${roomId} not found!`);
        return newState;
      }
      const messages = matrixRoom.getLiveTimeline().getEvents();
      console.log("initRoomMessages:", messages);
      const room = newState.rooms[roomId];
      if (!room) {
        throw new Error("Room not initialized yet");
      }
      room.info = messages;
      return newState;
      // const messages = getRoomMessages(roomId, onNewMessage);

      // todo add option to disable
      // return () => client.off(RoomEvent.Timeline, onMessage);
    }),

  sendMessageResponses: [],
  sendMessage: async (roomId, message): Promise<void> => {
    const client = get().client;
    if (!client) {
      throw new Error("Matrix client is not initialized!");
    }
    const sendMessageResponses = await sendMessage(client, roomId, message);
    set((state) => {
      return { ...state, sendMessageResponses };
    });
  },
}));

async function _start(
  client: MatrixClient,
  currentState: MatrixClientContextType,
): Promise<MatrixClientContextType> {
  await client.startClient();
  return initRooms(client, currentState);
}

function initRooms(
  client: MatrixClient,
  currentState: MatrixClientContextType,
): MatrixClientContextType {
  console.log("start init rooms");
  if (!client) {
    throw new Error("Matrix client is not initialized!");
  }
  const roomList: Room[] = getRooms(client);
  console.log("roomList", roomList);
  const newState: MatrixClientContextType = { ...currentState };
  roomList.forEach((room) => {
    newState.rooms[room.roomId] = {
      roomId: room.roomId,
      infoOther: room,
      info: [],
      roomState: undefined,
      messages: [],
    };
  });

  // Register event listener for new messages
  initMessageListener(client, currentState.onNewMessage);

  return newState;
}

export type LocalStorage = LoginResponse;

interface MatrixWindow extends Window {
  global: Window;
}

declare let window: MatrixWindow;
