import React, { useMemo } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import RootLayout from "./layout";
import LoadingPage from "./loading";
import NotFoundPage from "./not-found";
import Home from "./page";

export default function Pages(): JSX.Element {
  const isInitialized = true;
  return useMemo(() => {
    const pages = [
      {
        path: "/",
        content: <Home />,
      },
    ];
    return (
      <BrowserRouter>
        <RootLayout>
          <Routes>
            {isInitialized ? (
              pages.map((page) => {
                return (
                  <Route
                    key={page.path}
                    path={page.path}
                    element={page.content}
                  />
                );
              })
            ) : (
              <Route
                key='isLoading'
                path='*'
                element={<LoadingPage key='isLoading' />}
              />
            )}
            <Route
              key='notFound'
              path='*'
              element={<NotFoundPage key='notFound' />}
            />
          </Routes>
        </RootLayout>
      </BrowserRouter>
    );
  }, [isInitialized]);
}
