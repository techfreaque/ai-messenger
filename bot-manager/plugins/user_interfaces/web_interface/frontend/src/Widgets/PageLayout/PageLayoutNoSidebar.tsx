export function PageLayoutNoSidebar({
  children,
}: {
  children: JSX.Element;
}): JSX.Element {
  return (
    <div
      className={
        "dark flex h-screen w-full flex-col bg-sidebar font-geist-sans text-sidebar-foreground group-data-[variant=floating]:rounded-lg group-data-[variant=floating]:border group-data-[variant=floating]:border-sidebar-border group-data-[variant=floating]:shadow"
      }
    >
      {children}
    </div>
  );
}
