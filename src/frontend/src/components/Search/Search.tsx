import { ReactNode, useRef } from "react";
import style from "./Search.module.css";
import { Button } from "../Button/Button";

type SearchProps = {
  placeholder: string;
  buttonText: string;
  onSearch?: (text: string) => void;
};

export const Search = ({
  placeholder,
  buttonText,
  onSearch,
}: SearchProps): ReactNode => {
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <>
      <div className={style.search}>
        <input
          type="text"
          name="stockName"
          placeholder={placeholder}
          ref={inputRef}
        />
        <Button
          onClick={() =>
            onSearch &&
            inputRef.current != null &&
            onSearch(inputRef.current.value)
          }
          isWide={true}
        >
          {buttonText}
        </Button>
      </div>
    </>
  );
};
