import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";

import { NavigationMenuTop } from "./NavBar";

export function SplitHomeScreen({
  sideBarContent,
  mainContent,
}: {
  sideBarContent: JSX.Element;
  mainContent: JSX.Element;
}): JSX.Element {
  return (
    <main style={{ width: "100vw", height: "100vh" }}>
      <ResizablePanelGroup
        direction='horizontal'
        className='rounded-lg border md:min-w-[450px]'
      >
        <ResizablePanel defaultSize={25}>
          <div className='flex h-[200px] items-center justify-center p-6'>
            <span className='font-semibold'>{sideBarContent}</span>
          </div>
        </ResizablePanel>
        <ResizableHandle />
        <ResizablePanel defaultSize={90} className='z-50'>
          <div className='h-full w-full p-6 z-0'>
            <NavigationMenuTop />
            {mainContent}
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </main>
  );
}
