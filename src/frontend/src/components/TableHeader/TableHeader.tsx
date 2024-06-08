import { ReactNode } from "react";
import "./TableHeader.module.css";

type TableHeaderProps = {
  columns: string[];
};
export const TableHeader = ({ columns }: TableHeaderProps): ReactNode => {
  return (
    <>
      <thead>
        <tr>
          {columns.map((x) => (
            <th key={x}>{x}</th>
          ))}
        </tr>
      </thead>
    </>
  );
};
