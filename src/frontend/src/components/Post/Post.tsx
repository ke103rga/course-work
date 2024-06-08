import { ReactNode } from "react";
import style from "./Post.module.css";
import img from "../../assets/images/DEFAULT_NEWS_IMAGE.jpg";

type PostProps = {
  imageUrl: string;
  title: string;
  url: string;
  children: ReactNode;
};

export const Post = (props: PostProps): ReactNode => {
  return (
    <div className={style.post}>
      <img
        className={style.image}
        src={props.imageUrl}
        onError={(event) => {
          const image = event.target as HTMLImageElement;
          image.src = img;
        }}
      />
      <div className={style.textBlock}>
        <p className={style.header}>
          <a href={props.url} target="_blank">
            {props.title}
          </a>
        </p>
        <p className={style.text}>{props.children}</p>
      </div>
    </div>
  );
};
