import { ReactNode, useEffect, useState } from "react";
import { Header } from "../../components/Header/Header";
import { Table } from "../../components/Table/Table";
import { HorizontalLine } from "../../components/HorizontalLine/HorizontalLine";
import { Search } from "../../components/Search/Search";
import { getIncorrectRatedShares, getTickerHistory } from "../../utils/api";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

export type IncorrectRatedShare = {
  symbol: string;
  last_actual_quote: number;
  last_fair_quote: number;
  fair_real_ratio: number;
};

export const ScreenerPage = (): ReactNode => {
  const [overRated, setOverRated] = useState<{
    [key: number]: IncorrectRatedShare;
  }>({});
  const [underRated, setUnderRated] = useState<{
    [key: number]: IncorrectRatedShare;
  }>({});
  const [selectedShare, setSelectedShare] = useState<IncorrectRatedShare>();
  const [shareHistory, setHistory] = useState<{
    history: { [key: number]: { date: string; close: number } };
    fairHistory: { [key: number]: { date: string; fair_cost: number } };
  }>({ history: {}, fairHistory: {} });
  const [errorText, setErrorText] = useState<string>("");

  useEffect(() => {
    const fetchIncorrectRated = async () => {
      const data = await getIncorrectRatedShares();
      if (data.status != 200) {
        return;
      }

      const over = JSON.parse(data.data["overrated_shares"]) as {
        [key: number]: IncorrectRatedShare;
      };
      Object.entries(over).forEach(
        (entry) =>
          (over[parseInt(entry[0])] = {
            symbol: entry[1].symbol,
            last_actual_quote: entry[1].last_actual_quote,
            last_fair_quote: entry[1].last_fair_quote,
            fair_real_ratio: entry[1].fair_real_ratio,
          }),
      );
      const under = JSON.parse(data.data["underrated_shares"]) as {
        [key: number]: IncorrectRatedShare;
      };
      Object.entries(under).forEach(
        (entry) =>
          (under[parseInt(entry[0])] = {
            symbol: entry[1].symbol,
            last_actual_quote: entry[1].last_actual_quote,
            last_fair_quote: entry[1].last_fair_quote,
            fair_real_ratio: entry[1].fair_real_ratio,
          }),
      );
      setOverRated(over);
      setUnderRated(under);
    };

    fetchIncorrectRated();
  }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!selectedShare) {
        return;
      }

      const data = await getTickerHistory(selectedShare.symbol);
      if (data.status != 200) {
        setErrorText("Акция с указанным именем не найдена.");
        return;
      }

      if (errorText.length) {
        setErrorText("");
      }

      const history = {
        fairHistory: JSON.parse(data.data["fair_history"]) as {
          [key: number]: { date: string; fair_cost: number };
        },
        history: JSON.parse(data.data["history"]) as {
          [key: number]: { date: string; close: number };
        },
      };
      if (selectedShare.fair_real_ratio === 0) {
        selectedShare.last_fair_quote = Object.values(
          history.fairHistory,
        ).filter((x) => !!x.fair_cost)[
          Object.values(history.fairHistory).filter((x) => !!x.fair_cost)
            .length - 1
        ].fair_cost;
        selectedShare.last_actual_quote = Object.values(history.history)[
          Object.values(history.history).length - 1
        ].close;
        selectedShare.fair_real_ratio =
          selectedShare.last_fair_quote / selectedShare.last_actual_quote;
      }

      setHistory(history);
    };

    fetchHistory();
  }, [selectedShare]);

  const onShareSelected = (share: IncorrectRatedShare) => {
    setSelectedShare(share);
  };

  const onSearch = async (text: string) => {
    text = text.toUpperCase();
    const share = Object.values(overRated)
      .concat(Object.values(underRated))
      .filter((x) => x && x.symbol === text)[0];
    if (share) {
      setSelectedShare(share);
      return;
    }

    setSelectedShare({
      symbol: text,
      last_actual_quote: 0,
      last_fair_quote: 0,
      fair_real_ratio: 0,
    });
  };

  const columns = [
    "Название",
    "Рыночная стоимость",
    "Честная стоимость",
    "Честная/рыночная",
  ];
  const allDates = Array.from(
    new Set(
      Object.values(shareHistory.history)
        .map((x) => x.date)
        .concat(Object.values(shareHistory?.fairHistory).map((x) => x.date))
        .sort(),
    ),
  );
  const fairDataset = () => {
    const values = allDates.map((date) => {
      const dataItem = Object.values(shareHistory.fairHistory).find(
        (item) => item.date === date,
      );
      return dataItem ? dataItem.fair_cost : null;
    });

    const notNull = values.filter((x) => x);
    for (let i = 0; i < notNull.length - 1; i++) {
      const value1 = notNull[i] as number;
      const idx = values.indexOf(value1);
      const secondIdx = values.indexOf(notNull[i + 1]);
      const value2 = values[secondIdx] as number;
      for (let j = idx + 1; j < secondIdx; j++) {
        values[j] =
          ((value2 - value1) / (secondIdx - idx)) * (j - idx) + value1;
      }
    }

    return values;
  };

  return (
    <>
      <Header>Переоцененные акции</Header>
      <Table
        columns={columns}
        values={Object.values(overRated)}
        onClick={onShareSelected}
      ></Table>
      <HorizontalLine />
      <Header>Недооцененные акции</Header>
      <Table columns={columns} values={Object.values(underRated)}></Table>
      <HorizontalLine />
      <Header>Выбрать акцию</Header>
      <Search buttonText="Сравнить" placeholder="Поиск" onSearch={onSearch} />
      {errorText}
      {selectedShare && shareHistory && selectedShare.fair_real_ratio != 0 && (
        <>
          <Header>{selectedShare.symbol}</Header>
          {shareHistory && (
            <Line
              data={{
                labels: allDates.map((x) => new Date(x).toLocaleDateString()),
                datasets: [
                  {
                    label: "Реальная стоимость",
                    data: Object.values(shareHistory.history).map(
                      (x) => x.close,
                    ),
                    borderColor: "blue",
                    fill: true,
                  },
                  {
                    label: "Честная стоимость",
                    data: fairDataset(),
                    borderColor: "red",
                    fill: true,
                  },
                ],
              }}
            />
          )}
          <Table columns={columns} values={[selectedShare]}></Table>
        </>
      )}
    </>
  );
};
