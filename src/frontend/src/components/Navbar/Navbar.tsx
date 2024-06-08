import { ReactNode } from "react";
import { Logo } from "../Logo/Logo";
import style from "./Navbar.module.css";
import { Button } from "../Button/Button";
import { Link } from "react-router-dom";

export const Navbar = (): ReactNode => {
  return (
    <>
      <div className={style.navbar}>
        <Link to={"/"}>
          <Logo />
        </Link>
        <div className={style.buttonsWrapper}>
          <div className={style.navButtons}>
            <Link to={"/screener"}>
              <Button>Скринер акций</Button>
            </Link>
            <Link to={"/portfolio"}>
              <Button>Готовые портфолио</Button>
            </Link>
            <Link to={"/news"}>
              <Button>Новости трейдинга</Button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};
