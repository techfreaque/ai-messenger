"use client";

import { useEffect } from "react";
import React from "react";

import { matrixClient } from "../../context/MatrixClient";
import AppSidebar from "../SideBar/SideBarMain";

export function PageLayout({
  children,
}: {
  children: JSX.Element;
}): JSX.Element {
  const { init, selectedRoom, client, initRoom } = matrixClient();
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
  return (
    <div className={"font-geist-sans dark"}>
      <AppSidebar>{children}</AppSidebar>
    </div>
  );
}
