"use client";

import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Separator } from "@radix-ui/react-dropdown-menu";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import { ScrollArea } from "@radix-ui/react-scroll-area";

import { FileText } from "lucide-react";

interface SearchDialogProps {
  title?: string;
  open: boolean;
  placeholder?: string;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

interface SearchResultProps {
  id?: string;
  name: string;
}

const data: SearchResultProps[] = [
  {
    id: "1",
    name: "Customer Support Inquiry - Billing Issues"
  },
  {
    id: "2",
    name: "Project Kickoff Meeting - Q1 Marketing Strategy"
  },
  {
    id: "3",
    name: "Brainstorming Session - New Product Features Discussion"
  },
  {
    id: "4",
    name: "Weekly Standup - Engineering Team Updates & Goals"
  },
  {
    id: "5",
    name: "Research & Development - AI-powered Chatbot Enhancements"
  },
  {
    id: "6",
    name: "User Feedback Review - Improving App Usability & UX"
  },
  {
    id: "7",
    name: "Brainstorming Session - New Product Features Discussion"
  },
  {
    id: "8",
    name: "Weekly Standup - Engineering Team Updates & Goals"
  },
  {
    id: "9",
    name: "Research & Development - AI-powered Chatbot Enhancements"
  },
  {
    id: "10",
    name: "User Feedback Review - Improving App Usability & UX User Feedback Review - Improving App Usability & UX"
  }
];

export function SearchDialog({
  title = "Search",
  open,
  placeholder = "Search",
  setOpen
}: SearchDialogProps) {
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className=" border-2 p-0  max-w-2xl">
        <VisuallyHidden asChild>
          <DialogHeader>
            <DialogTitle className="text-center">{title}</DialogTitle>
          </DialogHeader>
        </VisuallyHidden>

        <div className="py-2.5">
          <Input
            placeholder={placeholder}
            className="text-xl pt-6 px-6 border-none focus-visible:ring-0 focus-visible:ring-offset-0 "
          />
        </div>

        <Separator className="border border-1 " />
        <ScrollArea className="max-h-72 overflow-y-scroll ">
          {data.map(({ name, id }) => (
            <SearchResult key={id} name={name} />
          ))}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}

const SearchResult: React.FC<SearchResultProps> = ({ name }) => {
  return (
    <div className="flex items-center gap-4 hover:bg-accent py-3 px-5 transition-colors ">
      <FileText className="size-6" />
      {/*  */}
      <h4 className=" flex-1 scroll-m-20 text-lg tracking-tight truncate">
        {name}
      </h4>
    </div>
  );
};
