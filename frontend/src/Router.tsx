import React from "react";
import { BrowserRouter } from "react-router-dom";

// Detect if running on GitHub Pages by checking the hostname
const isGithubPages = window.location.hostname.includes("github.io");

const Router = ({ children }: { children: React.ReactNode }) => {
  const basename = isGithubPages ? "/Home-Pulse-AI-V1.0" : "/";
  return <BrowserRouter basename={basename}>{children}</BrowserRouter>;
};

export default Router;