import { ReactNode } from "react";
import "./Header.module.css";

type HeaderProps = {
  children: ReactNode;
};

export const Header = ({ children }: HeaderProps): ReactNode => {
  return (
    <>
      <h2>{children}</h2>
    </>
  );
};
