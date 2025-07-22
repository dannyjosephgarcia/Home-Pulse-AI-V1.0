import React from 'react';
import { BrowserRouter, HashRouter } from 'react-router-dom';

const isGithubPages = import.meta.env.MODE === 'production';

const Router = ({ children }: { children: React.ReactNode }) => {
  // Use HashRouter for GitHub Pages
  return isGithubPages ? (
    <HashRouter>{children}</HashRouter>
  ) : (
    <BrowserRouter basename="/Home-Pulse-AI-V1.0">{children}</BrowserRouter>
  );
};

export default Router;