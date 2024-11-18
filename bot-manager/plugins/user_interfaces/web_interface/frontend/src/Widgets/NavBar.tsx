import type { ComponentPropsWithoutRef, ElementRef } from "react";
import { forwardRef } from "react";

import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "../components/ui/navigation-menu";
import { SidebarTrigger } from "../components/ui/sidebar";
import { cn } from "../lib/utils";

export interface NavigationMenuItem {
  href: string;
  title: string;
  children?: NavigationMenuItem[];
}

export function NavigationMenuTop({
  items,
  leftContent,
}: {
  items: NavigationMenuItem[];
  leftContent: JSX.Element;
}): JSX.Element {
  const renderMenuItems = (menuItems: NavigationMenuItem[]): JSX.Element[] => {
    return menuItems.map((item) => (
      <NavigationMenuItem key={item.href}>
        <NavigationMenuTrigger>{item.title}</NavigationMenuTrigger>
        {item.children && (
          <NavigationMenuContent className='z-50'>
            <ul className='grid gap-3 p-6 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]'>
              {renderMenuItems(item.children)}
            </ul>
          </NavigationMenuContent>
        )}
        {!item.children && (
          <NavigationMenuLink asChild>
            <a
              className='flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md'
              href={item.href}
            >
              <div className='mb-2 mt-4 text-lg font-medium'>{item.title}</div>
            </a>
          </NavigationMenuLink>
        )}
      </NavigationMenuItem>
    ));
  };

  return (
    <div className='flex w-full justify-between p-5'>
      <SidebarTrigger className='transition-all' />
      <div className='m-auto'>{leftContent}</div>
      <div className=''>
        <NavigationMenu>
          <NavigationMenuList>{renderMenuItems(items)}</NavigationMenuList>
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
