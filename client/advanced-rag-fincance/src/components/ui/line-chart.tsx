"use client";

import { CartesianGrid, Line, LineChart, XAxis } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter
} from "@/components/ui/card";
import {
  ChartContainer
} from "@/components/ui/chart";

const PREDEFINED_COLORS = [
  "#FF5733",
  "#33FF57",
  "#3357FF",
  "#FF33A8",
  "#A833FF",
  "#33FFF5",
  "#FFD700",
  "#FF8C00",
  "#ADFF2F",
  "#DC143C"
];

interface DatasetConfig {
  title?: string;
  description?: string;
  data?: Array<Record<string, any>>;
  config?: string[];
  source?: string;
}

export function LineChartComponent({ dataset }: { dataset: string | DatasetConfig }) {
  // Parse the dataset if it's a string (which is likely when coming from markdown)
  let parsedDataset: DatasetConfig = dataset as DatasetConfig;
  if (typeof dataset === "string") {
    try {
      parsedDataset = JSON.parse(dataset);
    } catch (e) {
      console.error("Failed to parse dataset:", e);
      parsedDataset = {};
    }
  }

  const {
    title = "",
    description = "",
    data = [],
    config = [],
    source = ""
  } = parsedDataset || {};

  // If there's no proper dataset, show a placeholder
  if (!data.length || !config.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title || "Chart"}</CardTitle>
          <CardDescription>
            {description || "No data available"}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex h-40 items-center justify-center text-muted-foreground">
          Chart data is missing or invalid
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>
          {description} {source && `(Source: ${source})`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={config}>
      <CardContent>
        <ChartContainer>
          <LineChart
            accessibilityLayer
            data={Array.isArray(data) ? data : []}
            margin={{ left: 12, right: 12 }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
            />
            {config.map((key: string, index: number) => (
              <Line
                key={key}
                dataKey={key}
                type="natural"
                stroke={PREDEFINED_COLORS[index % PREDEFINED_COLORS.length]}
                strokeWidth={2}
                dot={{
                  fill: PREDEFINED_COLORS[index % PREDEFINED_COLORS.length]
                }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        </ChartContainer>
      </CardContent>
        data might be assumed.
      </CardFooter>
    </Card>
  );
}
