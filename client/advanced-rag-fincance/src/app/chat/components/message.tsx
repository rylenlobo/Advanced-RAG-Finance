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
