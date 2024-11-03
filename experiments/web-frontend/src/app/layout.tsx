import "./globals.css";

import React from "react";

import { PageLayout } from "../Widgets/PageLayout/PageLayout";
export default function RootLayout({
  children,
}: Readonly<{
  children: JSX.Element;
}>): JSX.Element {
  return <PageLayout>{children}</PageLayout>;
}
