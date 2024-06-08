import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { MainPage } from "./views/MainPage/MainPage";
import { NewsPage } from "./views/NewsPage/NewsPage";
import { ScreenerPage } from "./views/ScreenerPage/ScreenerPage";
import { PortfolioPage } from "./views/PorfolioPage/PortfolioPage";
import { StrategyPage } from "./views/StrategyPage/StrategyPage";
import { Layout } from "./views/Layout/Layout";
import { AuthForm } from "./components/AuthForm/AuthForm";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <MainPage />,
      },
      {
        path: "/news",
        element: <NewsPage />,
      },
      {
        path: "/screener",
        element: <ScreenerPage />,
      },
      {
        path: "/portfolio",
        element: <PortfolioPage />,
      },
      {
        path: "/strategy",
        element: <StrategyPage />,
      },
      {
        path: "/auth",
        element: <AuthForm />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
