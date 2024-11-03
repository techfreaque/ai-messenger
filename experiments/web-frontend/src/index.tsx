import { createElement } from "react";
import { createRoot } from "react-dom/client";

import Pages from "./app/pages";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("no_root_element");
}
createRoot(rootElement).render(createElement(Pages));
