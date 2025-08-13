import React from "react";
import { HashRouter } from "react-router-dom";

const isGithubPages = window.location.hostname.includes("github.io");
const basename = isGithubPages ? "/Home-Pulse-AI-V1.0" : "/";

const Router = ({ children }: { children: React.ReactNode }) => {
  return <HashRouter basename={basename}>{children}</HashRouter>;
};

export default Router;