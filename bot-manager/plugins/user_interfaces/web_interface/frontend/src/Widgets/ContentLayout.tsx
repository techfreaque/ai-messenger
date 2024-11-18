export function ContentLayout({
  children,
}: {
  children: JSX.Element;
}): JSX.Element {
  return <div className='flex flex-1 flex-col gap-4 p-4 pt-0'>{children}</div>;
}

export function ContentContainer({
  children,
}: {
  children: JSX.Element;
}): JSX.Element {
  return <div className='rounded-xl bg-muted/50 p-5'>{children}</div>;
}
