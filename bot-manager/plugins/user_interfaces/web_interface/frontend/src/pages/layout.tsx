import type { BreadCrumbItem } from "../Widgets/PageLayout/PageLayout";
import { PageLayout } from "../Widgets/PageLayout/PageLayout";

export default function RootLayout({
  children,
  breadcrumbs,
}: {
  children: JSX.Element;
  breadcrumbs?: BreadCrumbItem[];
}): JSX.Element {
  return <PageLayout breadcrumbs={breadcrumbs}>{children}</PageLayout>;
}
