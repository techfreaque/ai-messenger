import { useEffect } from "react";
import "./global.css";
import Pages from "./Routes";
import { useBotStore } from "./state/botStore";
import { useMatrixClient } from "./state/MatrixClient";

export default function App(): JSX.Element {
  const { isLoggedIn, checkLogin } = useBotStore();
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
  return <Pages />;
}
