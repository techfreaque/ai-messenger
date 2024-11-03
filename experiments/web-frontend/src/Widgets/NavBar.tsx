"use client";

import type { ComponentPropsWithoutRef, ElementRef } from "react";
import React from "react";
import { forwardRef } from "react";

import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "../components/ui/navigation-menu";
import { SidebarTrigger, useSidebar } from "../components/ui/sidebar";
import type { MatrixRoom } from "../context/MatrixClient";
import { matrixClient } from "../context/MatrixClient";
import { cn } from "../lib/utils";

export function NavigationMenuTop(): JSX.Element {
  const { open } = useSidebar();
  const { selectedRoom, rooms } = matrixClient();

  const room: undefined | MatrixRoom = selectedRoom
    ? rooms[selectedRoom]
    : undefined;
  return (
    <div className='flex w-full justify-between p-5'>
      <SidebarTrigger className='transition-all' isVisible={!open} />
      <div className='m-auto'>Room: {room?.roomState?.roomId}</div>
      <div className=''>
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuTrigger>Invite</NavigationMenuTrigger>
              <NavigationMenuContent className='z-50'>
                <ul className='grid gap-3 p-6 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]'>
                  <li className='row-span-3'>
                    <NavigationMenuLink asChild>
                      <a
                        className='flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md'
                        href='/'
                      >
                        {/* <Icons.logo className='h-6 w-6' /> */}
                        <div className='mb-2 mt-4 text-lg font-medium'>
                          shadcn/ui
                        </div>
                        <p className='text-sm leading-tight text-muted-foreground'>
                          Beautifully designed components that you can copy and
                          paste into your apps. Accessible. Customizable. Open
                          Source.
                        </p>
                      </a>
                    </NavigationMenuLink>
                  </li>
                  <ListItem href='/docs' title='Introduction'>
                    Re-usable components built using Radix UI and Tailwind CSS.
                  </ListItem>
                  <ListItem href='/docs/installation' title='Installation'>
                    How to install dependencies and structure your app.
                  </ListItem>
                  <ListItem
                    href='/docs/primitives/typography'
                    title='Typography'
                  >
                    Styles for headings, paragraphs, lists...etc
                  </ListItem>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </div>
    </div>
  );
}

const ListItem = forwardRef<ElementRef<"a">, ComponentPropsWithoutRef<"a">>(
  ({ className, title, children, ...props }, ref) => {
    return (
      <li>
        <NavigationMenuLink asChild>
          <a
            ref={ref}
            className={cn(
              "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
              className,
            )}
            {...props}
          >
            <div className='text-sm font-medium leading-none'>{title}</div>
            <p className='line-clamp-2 text-sm leading-snug text-muted-foreground'>
              {children}
            </p>
          </a>
        </NavigationMenuLink>
      </li>
    );
  },
);
ListItem.displayName = "ListItem";
