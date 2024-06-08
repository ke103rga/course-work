import { ReactNode } from "react";
import { Navbar } from "../../components/Navbar/Navbar";
import { HorizontalLine } from "../../components/HorizontalLine/HorizontalLine";
import { Outlet } from "react-router";

export const Layout = (): ReactNode => (
  <div className="main">
    <Navbar />
    <HorizontalLine />
    <Outlet />
  </div>
);
