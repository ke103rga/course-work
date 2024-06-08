import { ReactNode } from "react";
import "./TableRow.module.css";
import { Ticker } from "../../views/MainPage/MainPage";
import { IncorrectRatedShare } from "../../views/ScreenerPage/ScreenerPage";
import { Share } from "../../views/PorfolioPage/PortfolioPage";

type TableRowProps = {
  row:
    | Ticker
    | IncorrectRatedShare
    | Omit<Share, "sector">
    | number[]
    | string[];
  onClick?: (share: IncorrectRatedShare) => void;
};

export const TableRow = ({ row, onClick }: TableRowProps): ReactNode => {
  return (
    <>
      <tr onClick={() => onClick && onClick(row as IncorrectRatedShare)}>
        {Object.values(row).map((x, i) => (
          <td key={i}>
            {typeof x === "number" ? x.toFixed(3) : x?.toString()}
          </td>
        ))}
      </tr>
    </>
  );
};
