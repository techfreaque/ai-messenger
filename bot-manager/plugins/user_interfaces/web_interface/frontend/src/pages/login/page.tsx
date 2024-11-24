import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useBotStore } from "../../state/botStore";
import Login from "../../Widgets/User/Login";

export default function LoginPage(): JSX.Element {
  const { isLoggedIn, routes } = useBotStore();
  const navigate = useNavigate();
  useEffect(() => {
    if (isLoggedIn) {
      navigate(routes.frontend.home);
    }
  }, [isLoggedIn]);
  return <Login />;
}
