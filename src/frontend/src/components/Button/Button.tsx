import { ReactNode } from "react";
import style from "./Button.module.css";

type ButtonProps = {
  isWide?: boolean;
  children?: ReactNode;
  onClick?: () => void;
};

export const Button = (props: ButtonProps): ReactNode => {
  return (
    <>
      <button
        className={style.btn + " " + (props.isWide ? style.wide : "")}
        onClick={props.onClick}
      >
        {props.children ? props.children : ""}
      </button>
    </>
  );
};
