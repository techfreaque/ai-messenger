import { useMemo } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useBotStore } from "./state/botStore";
import ConfigPage from "./pages/config/page";
import LoginPage from "./pages/login/page";
import RootLayout from "./pages/layout";
import LoadingPage from "./pages/loading";
import NotFoundPage from "./pages/not-found";
import HomePage from "./pages/page";
import RoomPage from "./pages/room/page";
import { PageLayoutNoSidebar } from "./Widgets/PageLayout/PageLayoutNoSidebar";

export default function Pages(): JSX.Element {
  const { isLoggedIn, routes } = useBotStore();
  return useMemo(() => {
    const pages = {
      home: {
        path: routes.frontend.home,
        content: <HomePage />,
        breadcrumbs: [{ label: "Home" }],
      },
      login: {
        path: routes.frontend.login,
        content: <LoginPage />,
        breadcrumbs: [{ label: "Login" }],
      },
      room: {
        path: routes.frontend.room,
        content: <RoomPage />,
        breadcrumbs: [
          { label: "Home", url: routes.frontend.home },
          { label: "Room" },
        ],
      },
      config: {
        path: routes.frontend.config,
        content: <ConfigPage />,
        breadcrumbs: [
          { label: "Home", url: routes.frontend.home },
          { label: "Bot Settings" },
        ],
      },
    };
    return (
      <BrowserRouter>
        <Routes>
          {isLoggedIn ? (
            <>
              {Object.values(pages).map((page) => {
                return (
                  <Route
                    key={page.path}
                    path={page.path}
                    element={
                      <RootLayout breadcrumbs={page.breadcrumbs}>
                        {page.content}
                      </RootLayout>
                    }
                  />
                );
              })}
              <Route
                key='notFound'
                path='*'
                element={
                  <RootLayout>
                    <NotFoundPage key='notFound' />
                  </RootLayout>
                }
              />
            </>
          ) : isLoggedIn === undefined ? (
            <Route
              key='isLoading'
              path='*'
              element={
                <PageLayoutNoSidebar>
                  <LoadingPage key='isLoading' />
                </PageLayoutNoSidebar>
              }
            />
          ) : (
            <>
              <Route path={pages.login.path} element={pages.login.content} />
              <Route
                key='anyOtherPage'
                path='*'
                element={<Navigate to={pages.login.path} />}
              />
            </>
          )}
        </Routes>
      </BrowserRouter>
    );
  }, [isLoggedIn]);
}
