import axios from "axios";

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 3000,
  validateStatus: () => true,
});

export const getNews = async (limit: number = 10) => {
  return await instance.get(`news/${limit}/`);
};

export const getMainTickers = async () => {
  return await instance.get("main_tickers_data/");
};

export const getIncorrectRatedShares = async () => {
  return await instance.get("incorrect_rated_shares");
};

export const getTickerHistory = async (slug: string) => {
  return await instance.get(`ticker_history/${slug}/`);
};

export const getStrategiesInfo = async () => {
  return await instance.get("strategies_info/");
};

export const getActualPortfolio = async () => {
  return await instance.get("actual_portfolio/");
};
