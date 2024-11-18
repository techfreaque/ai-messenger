import { useMemo } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "./state/authStore";
import ConfigPage from "./pages/config/page";
import LoginPage from "./pages/login/page";
import RootLayout from "./pages/layout";
import LoadingPage from "./pages/loading";
import NotFoundPage from "./pages/not-found";
import HomePage from "./pages/page";

export default function Pages(): JSX.Element {
  const { isLoggedIn, routes } = useAuthStore();
  return useMemo(() => {
    const pages = {
      home: {
        path: routes.home,
        content: <HomePage />,
        breadcrumbs: [{ label: "Home" }],
      },
      login: {
        path: routes.login,
        content: isLoggedIn ? <Navigate to={routes.config} /> : <LoginPage />,
        breadcrumbs: [{ label: "Home", url: routes.home }, { label: "Login" }],
      },
      config: {
        path: routes.config,
        content: isLoggedIn ? <ConfigPage /> : <Navigate to={routes.login} />,
        breadcrumbs: [
          { label: "Home", url: routes.home },
          { label: "Bot Settings" },
        ],
      },
    };
    return (
      <BrowserRouter>
        <Routes>
          {isLoggedIn ? (
            Object.values(pages).map((page) => {
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
            })
          ) : isLoggedIn === undefined ? (
            <Route
              key='isLoading'
              path='*'
              element={
                <RootLayout>
                  <LoadingPage key='isLoading' />
                </RootLayout>
              }
            />
          ) : (
            <Route
              path={pages.login.path}
              element={
                <RootLayout breadcrumbs={pages.login.breadcrumbs}>
                  {pages.login.content}
                </RootLayout>
              }
            />
          )}
          <Route
            key='notFound'
            path='*'
            element={
              <RootLayout>
                <NotFoundPage key='notFound' />
              </RootLayout>
            }
          />
        </Routes>
      </BrowserRouter>
    );
  }, [isLoggedIn]);
}
