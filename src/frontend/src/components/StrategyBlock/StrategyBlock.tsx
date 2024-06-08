import { ReactNode, useEffect, useState } from "react";
import style from "./StrategyBlock.module.css";
import { Header } from "../Header/Header";
import { Button } from "../Button/Button";
import { Link } from "react-router-dom";
import { Strategy } from "../../views/StrategyPage/StrategyPage";
import { getStrategiesInfo } from "../../utils/api";
import { Line } from "react-chartjs-2";
import { Table } from "../Table/Table";

export const StrategyBlock = (): ReactNode => {
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

  return (
    <div className={style.strategyBlock}>
      <div
        style={{
          width: "70vw",
        }}
      >
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
      </div>
      <div>
        <Header>
          Будьте впереди рынка с помощью наиболее эффективных акций, отобранных
          ИИ и способных превзойти индекс S&P 500
        </Header>
        <Link to={"/portfolio"}>
          <Button>Стратегия</Button>
        </Link>
      </div>
    </div>
  );
};
