import { ReactNode } from "react";
import style from "./CarouselPost.module.css";
import img from "../../assets/images/DEFAULT_NEWS_IMAGE.jpg";

type CarouselPostProps = {
  imageUrl: string;
  isSelected?: boolean;
  title: string;
  url: string;
  children: ReactNode;
};
export const CarouselPost = (props: CarouselPostProps): ReactNode => {
  return (
    <div
      className={style.post + " " + (props.isSelected ? style.selected : "")}
    >
      <img
        className={style.image + " " + (props.isSelected ? style.selected : "")}
        src={props.imageUrl}
        onError={(event) => {
          const image = event.target as HTMLImageElement;
          image.src = img;
        }}
      />
      <a href={props.url} target="_blank">
        <p
          className={
            style.header + " " + (props.isSelected ? style.selected : "")
          }
        >
          {props.title}
        </p>
      </a>
      <p
        className={style.text + " " + (props.isSelected ? style.selected : "")}
      >
        {props.children}
      </p>
    </div>
  );
};
