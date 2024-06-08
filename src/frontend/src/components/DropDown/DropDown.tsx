import closed from "../../assets/dropDown/closed.svg";
import dropped from "../../assets/dropDown/dropped.svg";
import { ReactElement, ReactNode, useState } from "react";
import style from "./DropDown.module.css";

type DropDownProps = {
  header: string;
  children: ReactNode;
};

export const DropDown = (props: DropDownProps): ReactElement => {
  const [isDropped, setDrop] = useState(false);
  return (
    <>
      <div className={style.dropDown}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <img
            style={{ maxWidth: "3vw" }}
            src={isDropped ? dropped : closed}
            onClick={() => setDrop(!isDropped)}
          />
          <p>{props.header}</p>
        </div>
        {isDropped && props.children}
      </div>
    </>
  );
};
