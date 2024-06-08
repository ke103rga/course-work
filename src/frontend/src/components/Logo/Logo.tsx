import style from "./Logo.module.css";
import logo from "../../assets/logo/logo.svg";

export const Logo = () => {
  return (
    <>
      <img className={style.logo} src={logo}></img>
    </>
  );
};
