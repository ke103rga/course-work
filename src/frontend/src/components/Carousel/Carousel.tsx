import { ReactNode, useState } from "react";
import style from "./Carousel.module.css";
import { CarouselPost } from "../CarouselPost/CarouselPost";
import Flickity from "react-flickity-component";
import "./Carousel.module.css";
import "./flickity.css";
import { PostType } from "../../views/NewsPage/NewsPage";

type CarouselProps = {
  posts: PostType[];
};

export const Carousel = ({ posts }: CarouselProps): ReactNode => {
  const [selectedIndex, select] = useState<number>(
    Math.floor(posts?.length / 2),
  );
  const options = {
    initialIndex: selectedIndex,
  };

  const onChange = (index: number) => {
    select(index);
  };

  return (
    <Flickity
      className={style.carousel}
      reloadOnUpdate={true}
      options={options}
      elementType="div"
      disableImagesLoaded={false}
      flickityRef={(f) => f.on("settle", (idx: number) => onChange(idx))}
    >
      {posts?.map((x: PostType, i: number) => (
        <CarouselPost
          key={i}
          url={x.article_url}
          title={x.title}
          imageUrl={x.image_url}
          isSelected={selectedIndex === i}
        >
          {x.description}
        </CarouselPost>
      ))}
    </Flickity>
  );
};
