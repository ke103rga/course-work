import { ReactNode, useEffect, useState } from "react";
import { Header } from "../../components/Header/Header";
import { Doughnut, Line } from "react-chartjs-2";
import { getActualPortfolio, getStrategiesInfo } from "../../utils/api";
import { Strategy } from "../StrategyPage/StrategyPage";
import { DropDown } from "../../components/DropDown/DropDown";
import { Table } from "../../components/Table/Table";

export type Share = {
  sector: string;
  stock_name: string;
  part: number;
};

const translation: { [key: string]: string } = {
  Utilities: "Коммунальные услуги, энергетика",
  Telecommunications: "Телекоммуникация",
  Technology: "Технологии",
  "Real Estate": "Недвижимость",
  Energy: "Энергетика, нефтегазовый сектор",
  "Consumer Staples": "Потребительские товары первой необходимости",
  Industrials: "Промышленный сектор",
  "Consumer Discretionary": "Потребительское товары второй необходимости",
  Finance: "Финансовый сектор",
  "Health Care": "Здравоохранение",
  Miscellaneous: "Прочие",
  "Basic Materials": "Сырьевой сектор",
};

export const PortfolioPage = (): ReactNode => {
  const [shares, setShares] = useState<Share[]>([]);
  const [strategies, setStrategies] = useState<{
    strategy_prices: { [key: number]: Strategy };
    strategy_stats: {
      [key: number]: { total_return: number; daily_sharpe: number };
    };
  }>();
  useEffect(() => {
    const fetchStrategy = async () => {
      const data = await getStrategiesInfo();
      data.data["strategy_prices"] = JSON.parse(data.data["strategy_prices"]);
      data.data["strategy_stats"] = JSON.parse(data.data["strategy_stats"]);
      setStrategies(data.data);
    };

    fetchStrategy();
  }, []);
  useEffect(() => {
    const fetchPortfolio = async () => {
      const data = await getActualPortfolio();
      setShares(data.data["actual_portfolio"]);
    };

    fetchPortfolio();
  }, []);

  const groupShares = (shares: Share[]) => {
    const groups: { [groupName: string]: Share[] } = {};
    shares.forEach((x) => {
      if (x.sector in groups) {
        groups[x.sector].push(x);
      } else {
        groups[x.sector] = [x];
      }
    });

    const sums: number[] = [];
    Object.values(groups).forEach((group) => {
      sums.push(0);
      group.forEach((share) => (sums[sums.length - 1] += share.part));
    });

    return { groups: Object.keys(groups), sums };
  };
  const { groups, sums } = groupShares(shares);
  const getRandomColor = () => {
    return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
  };

  const colors = Array.from({ length: sums.length }, () => getRandomColor());
  return (
    <>
      <Header>Состав портфолио</Header>
      <div style={{ width: "60%" }}>
        <Doughnut
          data={{
            labels: groups
              .filter((x) => typeof x === "string")
              .map((x) => translation[x]),
            datasets: [
              {
                data: sums,
                backgroundColor: colors,
              },
            ],
          }}
        />
      </div>
      {groups
        .filter((x) => typeof x === "string")
        .map((x, i) => (
          <DropDown header={x + `, ${translation[x]}`} key={i}>
            <Table
              columns={["Название", "Доля от портфеля"]}
              values={shares
                .filter((share) => share.sector === x)
                .map((x) => {
                  return { stock_name: x.stock_name, part: x.part };
                })}
            />
          </DropDown>
        ))}
      {strategies && (
        <Line
          data={{
            labels: Object.values(strategies.strategy_prices).map((x) =>
              new Date(Date.parse(x.date)).toLocaleDateString(),
            ),
            datasets: [
              {
                label: "S&P500",
                data: Object.values(strategies.strategy_prices).map(
                  (x) => x.spy,
                ),
              },
              {
                label: "Стратегия",
                data: Object.values(strategies.strategy_prices).map(
                  (x) => x.strategy_1,
                ),
              },
            ],
          }}
        />
      )}
      {strategies && (
        <Table
          columns={["Доход", "Опережение S&P 500", "Шарп"]}
          values={[
            [
              (strategies.strategy_stats[0].total_return * 100).toFixed(2) +
                "%",

              (
                (strategies.strategy_stats[0].total_return -
                  strategies.strategy_stats[1].total_return) *
                100
              ).toFixed(2) + "%",
              strategies.strategy_stats[0].daily_sharpe.toFixed(2),
            ],
          ]}
        />
      )}
    </>
  );
};
