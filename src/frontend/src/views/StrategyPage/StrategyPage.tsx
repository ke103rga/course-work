import { ReactNode, useEffect, useState } from "react";
import { Header } from "../../components/Header/Header";
import { getStrategiesInfo } from "../../utils/api";
import { Line } from "react-chartjs-2";

export type Strategy = {
  date: string;
  strategy_1: number;
  spy: number;
};

export const StrategyPage = (): ReactNode => {
  const [strategies, setStrategies] = useState<{
    strategy_prices: { [key: number]: Strategy };
  }>({ strategy_prices: {} });
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
    <>
      <Header>Динамика стратегий</Header>
      <Line
        data={{
          labels: Object.values(strategies.strategy_prices).map((x) =>
            new Date(Date.parse(x.date)).toLocaleDateString(),
          ),
          datasets: [
            {
              label: "S&P500",
              data: Object.values(strategies.strategy_prices).map((x) => x.spy),
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
    </>
  );
};
