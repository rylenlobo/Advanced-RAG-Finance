import Markdown from "markdown-to-jsx";

import { Separator } from "@/components/ui/separator";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import {
  TypographyH1,
  TypographyH2,
  TypographyH3,
  TypographyH4,
  TypographyP,
  TypographyInlineCode,
  TypographyList,
  TypographyListItem,
  TypographyBlockquote
} from "@/components/ui/typography/typography";
import type { Message } from "@/network/fetch-messages";
import { cn } from "@/lib/utils";
import { LineChartComponent } from "@/components/ui/line-chart";

export function Message({ message }: { message: Message }): React.ReactNode {
  const options = {
    overrides: {
      table: {
        component: Table
      },
      tbody: {
        component: TableBody
      },
      caption: {
        component: TableCaption
      },
      td: {
        component: TableCell
      },
      thead: {
        component: TableHeader
      },
      th: {
        component: TableHead
      },
      tr: {
        component: TableRow
      },
      h1: {
        component: TypographyH1
      },
      h2: {
        component: TypographyH2
      },
      h3: {
        component: TypographyH3
      },
      h4: {
        component: TypographyH4
      },
      p: {
        component: TypographyP
      },
      code: {
        component: TypographyInlineCode
      },
      ul: {
        component: TypographyList
      },
      li: {
        component: TypographyListItem
      },
      blockquote: {
        component: TypographyBlockquote
      },
      hr: {
        component: Separator
      }
    }
  };

  // LineChartComponent: {
  //         component: LineChartComponent
  //       },
  //       // Add an alias for lowercase version that might be generated
  //       linechartcomponent: {
  //         component: LineChartComponent
  //       }

  if (message.isLoading) {
    return (
      <div
        className={cn(
          "flex w-full items-start max-w-3xl mx-auto animate-in fade-in-0 duration-200",
          "justify-start"
        )}
      >
        <div className="mb-6 w-full px-4 py-2 pl-0">
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 animate-pulse rounded-full bg-gray-400"></div>
            <div className="h-2 w-2 animate-pulse rounded-full bg-gray-400 delay-150"></div>
            <div className="h-2 w-2 animate-pulse rounded-full bg-gray-400 delay-300"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex w-full items-start  max-w-3xl mx-auto animate-in fade-in-0 duration-200",
        message.role === "user" ? "justify-end" : "justify-start"
      )}
    >
      {/* Chat Bubble */}
      <div
        className={cn(
          "px-4 py-2 ",
          message.role === "assistant"
            ? "w-full pl-0 mb-6"
            : "bg-secondary max-w-[75%]  rounded-lg "
        )}
      >
        <Markdown options={options}>{message.content}</Markdown>
      </div>
    </div>
  );
}
