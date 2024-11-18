import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "../../components/ui/breadcrumb";
import { Separator } from "../../components/ui/separator";
import { SidebarInset, SidebarTrigger } from "../../components/ui/sidebar";
import AppSidebar from "../SideBar/SideBarMain";

export interface BreadCrumbItem {
  label: string;
  url?: string;
}

export function PageLayout({
  children,
  breadcrumbs,
}: {
  children: JSX.Element;
  breadcrumbs: BreadCrumbItem[] | undefined;
}): JSX.Element {
  return (
    <div className={"font-geist-sans dark flex w-full text-sidebar-foreground"}>
      <AppSidebar>
        <div className='w-full'>
          <SidebarInset>
            <header className='flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12'>
              <div className='flex items-center gap-2 px-4'>
                <SidebarTrigger className='-ml-1' />
                <Separator orientation='vertical' className='mr-2 h-4' />
                <Breadcrumb>
                  <BreadcrumbList>
                    {breadcrumbs?.map((item, index) => (
                      <>
                        {index !== 0 && (
                          <BreadcrumbSeparator className='hidden md:block' />
                        )}
                        {index === breadcrumbs.length - 1 ? (
                          <BreadcrumbItem>
                            <BreadcrumbPage>{item.label}</BreadcrumbPage>
                          </BreadcrumbItem>
                        ) : (
                          <BreadcrumbItem className='hidden md:block'>
                            <BreadcrumbLink to={item.url}>
                              {item.label}
                            </BreadcrumbLink>
                          </BreadcrumbItem>
                        )}
                      </>
                    ))}
                  </BreadcrumbList>
                </Breadcrumb>
              </div>
            </header>
            {children}
          </SidebarInset>
        </div>
      </AppSidebar>
    </div>
  );
}
