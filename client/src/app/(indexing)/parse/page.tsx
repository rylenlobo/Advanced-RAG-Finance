"use client";

import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Image from "next/image";
import { Button } from "@/components/ui/button";

export default function ParsePage() {
  const [showMarkdown, setShowMarkdown] = useState(true);

  const textContent = `
# Microsoft Annual Report Highlights

## Financial Performance
- Revenue: $168.1 billion (up 18% year-over-year)
- Operating income: $69.9 billion (up 19% year-over-year)
- Net income: $61.3 billion (up 18% year-over-year)

## Key Business Segments
1. Productivity and Business Processes
2. Intelligent Cloud
3. More Personal Computing

## Strategic Initiatives
- Continued investment in AI and cloud technologies
- Expansion of Microsoft 365 and Teams capabilities
- Focus on cybersecurity solutions

---

## Product Highlights

### Azure
Azure revenue grew 40% year-over-year, driven by strong demand for our cloud computing services.

### Microsoft 365
Microsoft 365 consumer subscribers increased to 58.4 million, up 15% year-over-year.

### Gaming
Xbox content and services revenue increased by 2%, with growth in Xbox Game Pass subscriptions.

---

## Future Outlook

Microsoft remains committed to innovation and digital transformation across industries. We anticipate continued growth in cloud services, AI integration, and expansion of our productivity tools.
  `;

  const tableContent = `
| Segment | Revenue (in billions) | Growth (YoY) |
|---------|----------------------:|-------------:|
| Productivity and Business Processes | $53.9 | 17% |
| Intelligent Cloud | $60.1 | 25% |
| More Personal Computing | $54.1 | 11% |

**Table Summary:** This table presents the revenue breakdown for Microsoft's three main business segments, showcasing strong growth across all areas, with Intelligent Cloud leading in both revenue and growth rate.

---

| Product | Active Users (millions) | YoY Growth |
|---------|------------------------:|------------|
| Office 365 | 345 | 15% |
| Teams | 270 | 30% |
| Dynamics 365 | 20 | 25% |
| LinkedIn | 774 | 11% |

**Table Summary:** This table shows the active user base for key Microsoft products and services, highlighting significant growth across the portfolio.

---

| Region | Revenue (in billions) | % of Total Revenue |
|--------|----------------------:|-------------------:|
| United States | $82.4 | 49% |
| Europe, Middle East, and Africa | $38.7 | 23% |
| Asia Pacific | $33.6 | 20% |
| Other | $13.4 | 8% |

**Table Summary:** This table breaks down Microsoft's revenue by geographic region, illustrating the company's global presence and the significance of the U.S. market.
  `;

  const chartContent = `
![Microsoft Revenue by Segment](/placeholder.svg?height=300&width=500)

**Chart Summary:** The pie chart illustrates the revenue distribution across Microsoft's three main business segments. Intelligent Cloud represents the largest portion at 36%, followed by More Personal Computing at 32%, and Productivity and Business Processes at 32%. This balanced distribution demonstrates Microsoft's successful diversification strategy.

---

![Year-over-Year Growth by Segment](/placeholder.svg?height=300&width=500)

**Chart Summary:** This bar chart compares the year-over-year growth rates for each of Microsoft's main business segments. Intelligent Cloud shows the highest growth rate at 25%, followed by Productivity and Business Processes at 17%, and More Personal Computing at 11%.

---

![Microsoft Stock Price Trend](/placeholder.svg?height=300&width=500)

**Chart Summary:** This line chart displays Microsoft's stock price trend over the past five years. The chart shows a steady upward trajectory, reflecting the company's strong financial performance and investor confidence in its long-term strategy.
  `;

  return (
    <div className="w-full h-screen p-5 bg-background">
      <Tabs defaultValue="text" className="w-full h-full flex flex-col">
        <div className="flex justify-between">
          <TabsList className="grid w-1/3 grid-cols-3 mb-4">
            <TabsTrigger value="text">Text</TabsTrigger>
            <TabsTrigger value="tables">Tables</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
          </TabsList>
          <Button disabled>Embed</Button>
        </div>

        <h2 className="text-3xl font-semibold tracking-tight py-2">Results</h2>
        <p className="font-semibold leading-7 [&:not(:first-child)]:mt-1 mb-4">
          microsoft-annual-report.pdf
        </p>
        <Card className="w-full flex-grow overflow-hidden">
          <CardContent className="p-6 h-full flex flex-col">
            <div className="flex justify-end mb-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="markdown-mode"
                  checked={showMarkdown}
                  onCheckedChange={setShowMarkdown}
                />
                <Label htmlFor="markdown-mode">Show as Markdown</Label>
              </div>
            </div>
            <div className="overflow-auto flex-grow">
              <TabsContent value="text" className="h-full">
                {showMarkdown ? (
                  <div className="prose dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {textContent}
                    </ReactMarkdown>
                    <Separator className="my-4" />
                    <p className="text-sm text-muted-foreground">Pages: 1-3</p>
                  </div>
                ) : (
                  <div>
                    <pre className="whitespace-pre-wrap">{textContent}</pre>
                    <Separator className="my-4" />
                    <p className="text-sm text-muted-foreground">Pages: 1-3</p>
                  </div>
                )}
              </TabsContent>
              <TabsContent value="tables" className="h-full">
                {showMarkdown ? (
                  <div className="prose dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {tableContent}
                    </ReactMarkdown>
                    <Separator className="my-4" />
                    <p className="text-sm text-muted-foreground">Pages: 5-7</p>
                  </div>
                ) : (
                  <div>
                    <pre className="whitespace-pre-wrap">{tableContent}</pre>
                    <Separator className="my-4" />
                    <p className="text-sm text-muted-foreground">Pages: 5-7</p>
                  </div>
                )}
              </TabsContent>
              <TabsContent value="charts" className="h-full">
                {showMarkdown ? (
                  <div className="prose dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {chartContent}
                    </ReactMarkdown>
                    <Separator className="my-4" />
                    <p className="text-sm text-muted-foreground">Pages: 8-10</p>
                  </div>
                ) : (
                  <div>
                    <Image
                      src="/placeholder.svg?height=300&width=500"
                      alt="Microsoft Revenue by Segment"
                      width={500}
                      height={300}
                    />
                    <p className="mt-4">
                      The pie chart illustrates the revenue distribution across
                      Microsoft's three main business segments. Intelligent
                      Cloud represents the largest portion at 36%, followed by
                      More Personal Computing at 32%, and Productivity and
                      Business Processes at 32%. This balanced distribution
                      demonstrates Microsoft's successful diversification
                      strategy.
                    </p>
                    <Separator className="my-4" />
                    <Image
                      src="/placeholder.svg?height=300&width=500"
                      alt="Year-over-Year Growth by Segment"
                      width={500}
                      height={300}
                    />
                    <p className="mt-4">
                      This bar chart compares the year-over-year growth rates
                      for each of Microsoft's main business segments.
                      Intelligent Cloud shows the highest growth rate at 25%,
                      followed by Productivity and Business Processes at 17%,
                      and More Personal Computing at 11%.
                    </p>
                    <Separator className="my-4" />
                    <Image
                      src="/placeholder.svg?height=300&width=500"
                      alt="Microsoft Stock Price Trend"
                      width={500}
                      height={300}
                    />
                    <p className="mt-4">
                      This line chart displays Microsoft's stock price trend
                      over the past five years. The chart shows a steady upward
                      trajectory, reflecting the company's strong financial
                      performance and investor confidence in its long-term
                      strategy.
                    </p>
                    <Separator className="my-4" />
                    <p className="text-sm text-muted-foreground">Pages: 8-10</p>
                  </div>
                )}
              </TabsContent>
            </div>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
}
