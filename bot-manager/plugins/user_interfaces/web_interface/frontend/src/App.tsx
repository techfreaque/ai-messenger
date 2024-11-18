import { useEffect } from "react";
import "./global.css";
import Pages from "./Routes";
import { useAuthStore } from "./state/authStore";
import { useMatrixClient } from "./state/MatrixClient";

export default function App(): JSX.Element {
  const { isLoggedIn, checkLogin } = useAuthStore();
  const { init, selectedRoom, client, initRoom } = useMatrixClient();

  useEffect(() => {
    void checkLogin();
  }, [isLoggedIn]);

  useEffect(() => {
    if (!client) {
      void init();
    }
  }, [client, init]);
  useEffect(() => {
    if (selectedRoom) {
      initRoom(selectedRoom);
    }
  }, [initRoom, selectedRoom]);

  if (isLoggedIn === undefined) {
    return <p>Loading...</p>;
  }
  return <Pages />;
}
