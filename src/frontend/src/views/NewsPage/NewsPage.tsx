import { ReactNode, useEffect, useState } from "react";
import { Post } from "../../components/Post/Post";
import { getNews } from "../../utils/api";

export type PostType = {
  image_url: string;
  title: string;
  description: string;
  article_url: string;
};

export const NewsPage = (): ReactNode => {
  const [news, setNews] = useState<PostType[]>([]);

  useEffect(() => {
    const fetchNews = async () => {
      const data = await getNews(import.meta.env.VITE_COUNT_NEWS_IN_NEWS_PAGE);
      setNews(data.data["news"]);
    };
    fetchNews();
  }, []);
  return (
    <>
      {news.map((x, i) => (
        <Post
          imageUrl={x.image_url}
          title={x.title}
          key={i}
          url={x.article_url}
        >
          {x.description}
        </Post>
      ))}
    </>
  );
};
