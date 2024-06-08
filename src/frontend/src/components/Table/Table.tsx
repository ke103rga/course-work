import { ReactNode } from "react";
import { TableHeader } from "../TableHeader/TableHeader";
import { TableRow } from "../TableRow/TableRow";
import style from "./Table.module.css";
import { Ticker } from "../../views/MainPage/MainPage";
import { IncorrectRatedShare } from "../../views/ScreenerPage/ScreenerPage";
import { Share } from "../../views/PorfolioPage/PortfolioPage";

type TableProps = {
  columns: string[];
  values:
    | Ticker[]
    | IncorrectRatedShare[]
    | Omit<Share, "sector">[]
    | number[][]
    | string[][];
  onClick?: (share: IncorrectRatedShare) => void;
};

export const Table = (props: TableProps): ReactNode => {
  return (
    <>
      <div className={style.tableWrapper}>
        <table>
          <TableHeader columns={props.columns} />
          <tbody>
            {props.values.map((x, i) => (
              <TableRow key={i} row={x} onClick={props.onClick} />
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
};
