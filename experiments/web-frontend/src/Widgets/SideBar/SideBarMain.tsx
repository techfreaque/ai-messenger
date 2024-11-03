"use client";

import { IconAffiliate, IconHearts, IconRobot } from "@tabler/icons-react";
import React from "react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
} from "../../components/ui/sidebar";
import { NavigationMenuTop } from "../NavBar";
import RoomList from "../RoomList";

export default function AppSidebar({
  children,
}: {
  children: JSX.Element;
}): JSX.Element {
  return (
    <SidebarProvider>
      <AppSidebarContent>{children}</AppSidebarContent>
    </SidebarProvider>
  );
}

export function AppSidebarContent({
  children,
}: {
  children: JSX.Element;
}): JSX.Element {
  return (
    <>
      <Sidebar>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Start a new chat</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton asChild>
                    <a href='#hello'>
                      <IconAffiliate
                        style={{ width: "25px", height: "25px" }}
                      />
                      Explore Groups
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton asChild>
                    <a href='#hello'>
                      <IconRobot style={{ width: "25px", height: "25px" }} />
                      Explore Bots
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton asChild>
                    <a href='#hello'>
                      <IconHearts style={{ width: "25px", height: "25px" }} />{" "}
                      Explore Humans
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
          <RoomList />
        </SidebarContent>
      </Sidebar>
      <main className='w-full bg-primary'>
        <NavigationMenuTop />
        {children}
      </main>
    </>
  );
}
