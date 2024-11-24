import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "../components/ui/sidebar";
import { useMatrixClient } from "../state/MatrixClient";

export default function RoomList(): JSX.Element {
  const { selectedRoom, rooms, setSelectedRoom } = useMatrixClient();
  console.log("selectedRoom", selectedRoom);
  return (
    <SidebarGroup>
      <SidebarGroupLabel>Your chats</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {Object.values(rooms).map((room) => {
            return (
              <SidebarMenuItem key={room.roomId}>
                <SidebarMenuButton asChild>
                  <button
                    className={
                      selectedRoom === room.roomId ? "background-cyan-700" : ""
                    }
                    onClick={(): void => {
                      setSelectedRoom(room.roomId);
                    }}
                  >
                    {room.roomId}
                  </button>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
