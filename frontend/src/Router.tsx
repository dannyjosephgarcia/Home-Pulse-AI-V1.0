import React from "react";
import { BrowserRouter } from "react-router-dom";

const isGithubPages = window.location.hostname.includes("github.io");
const basename = isGithubPages ? "/Home-Pulse-AI-V1.0" : "/";

const Router = ({ children }: { children: React.ReactNode }) => {
  return <BrowserRouter basename={basename}>{children}</BrowserRouter>;
};

export default Router;