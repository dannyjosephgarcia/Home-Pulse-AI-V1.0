import React from "react";
import { HashRouter } from "react-router-dom";

const Router = ({ children }: { children: React.ReactNode }) => {
  return <HashRouter>{children}</HashRouter>;
};

export default Router;