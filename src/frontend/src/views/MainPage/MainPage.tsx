import { ReactNode, useEffect, useState } from "react";
import { Button } from "../../components/Button/Button";
import { Header } from "../../components/Header/Header";
import { HorizontalLine } from "../../components/HorizontalLine/HorizontalLine";
import { Table } from "../../components/Table/Table";
import { Carousel } from "../../components/Carousel/Carousel";
import { StrategyBlock } from "../../components/StrategyBlock/StrategyBlock";
import { PostType } from "../NewsPage/NewsPage";
import { getMainTickers, getNews } from "../../utils/api";
import { Link } from "react-router-dom";

export type Ticker = {
  name: string;
  last: number;
  max: number;
  min: number;
  date: Date | string;
  change: number;
  relative_change: number;
};

export const MainPage = (): ReactNode => {
  const [news, setNews] = useState<PostType[]>([]);
  const [tickers, setTickers] = useState<{ [key: number]: Ticker }>({});
  useEffect(() => {
    const fetchNews = async () => {
      const data = await getNews(import.meta.env.VITE_COUNT_NEWS_IN_CAROUSEL);
      setNews(data.data["news"]);
    };

    fetchNews();

    const fetchMainTickers = async () => {
      const data = await getMainTickers();
      setTickers(JSON.parse(data.data["main_tickers_data"]));
    };

    fetchMainTickers();
  }, []);

  const columns = [
    "Название",
    "Послед",
    "Макс.",
    "Мин.",
    "Дата",
    "Изм.",
    "Изм. %",
  ];

  return (
    <>
      <Header>Котировки акций</Header>
      <Table columns={columns} values={Object.values(tickers)} />
      <Link to={"/screener"}>
        <Button isWide={true}>Сравнить с честной стоимостью</Button>
      </Link>
      <HorizontalLine />
      <Header>Новости</Header>
      <Carousel posts={news}></Carousel>
      <HorizontalLine />
      <Header>Инвестиционная стратегия</Header>
      <StrategyBlock />
    </>
  );
};
