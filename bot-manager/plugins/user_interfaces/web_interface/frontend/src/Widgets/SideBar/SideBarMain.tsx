import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarProvider,
  SidebarRail,
} from "../../components/ui/sidebar";
import { Bot, GalleryVerticalEnd, PieChart, Settings2 } from "lucide-react";
import { TeamSwitcher } from "../../components/team-switcher";
import { NavMain } from "../../components/nav-main";
import { NavSettings } from "../../components/nav-projects";
import { NavUser } from "./SideBarUser";
import { IconLungs, IconPlus, IconUsersGroup } from "@tabler/icons-react";
import { useAuthStore } from "../../state/authStore";

export default function AppSidebar({
  children,
}: {
  children: JSX.Element;
}): JSX.Element {
  return (
    <SidebarProvider pageContent={children}>
      <AppSidebarContent />
    </SidebarProvider>
  );
}

export function AppSidebarContent(
  props: React.ComponentProps<typeof Sidebar>,
): JSX.Element {
  const data = useGetSidebarData();
  return (
    <Sidebar collapsible='icon' {...props}>
      <SidebarHeader>
        <TeamSwitcher bots={data.bots} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain messages={data.messages} />
        <NavSettings settings={data.settings} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}

interface SideBarUserData {
  name: string;
  email: string;
  avatar: string;
}
export interface SideBarBotData {
  name: string;
  logo: React.ElementType;
  plan: string;
}
export interface SideBarMessagesData {
  title: string;
  url: string;
  icon: React.ElementType;
  isActive?: boolean;
  items: {
    title: string;
    url: string;
  }[];
}

export interface SideBarSettingsData {
  name: string;
  url: string;
  icon: React.ElementType;
}

interface SideBarData {
  user: SideBarUserData;
  bots: SideBarBotData[];
  messages: SideBarMessagesData[];
  settings: SideBarSettingsData[];
}

function useGetSidebarData(): SideBarData {
  const { routes } = useAuthStore();
  return {
    user: {
      name: "shadcn",
      email: "m@example.com",
      avatar: "/avatars/shadcn.jpg",
    },
    bots: [
      {
        name: "Acme Inc",
        logo: GalleryVerticalEnd,
        plan: "Enterprise",
      },
    ],
    messages: [
      {
        title: "Start new chat",
        url: "#",
        icon: IconPlus,
        isActive: true,
        items: [
          {
            title: "Explore Groups",
            url: "#",
          },
          {
            title: "Explore Bots",
            url: "#",
          },
          {
            title: "Explore Humans",
            url: "#",
          },
        ],
      },
      {
        title: "Bots",
        url: "#",
        icon: Bot,
        items: [
          {
            title: "Genesis",
            url: "#",
          },
        ],
      },
      {
        title: "People",
        url: "#",
        icon: IconLungs,
        items: [
          {
            title: "Introduction",
            url: "#",
          },
        ],
      },
      {
        title: "Groups",
        url: "#",
        icon: IconUsersGroup,
        items: [
          {
            title: "General",
            url: "#",
          },
        ],
      },
    ],
    settings: [
      {
        name: "Bot Settings",
        url: routes.config,
        icon: Settings2,
      },
      {
        name: "Bot Character",
        url: "#",
        icon: PieChart,
      },
    ],
  };
}
