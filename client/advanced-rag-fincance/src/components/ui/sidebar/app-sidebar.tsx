import * as React from "react";
import { NavPreviousChatsList } from "@/components/ui/sidebar/nav-previous-chats";
import { NavUser } from "@/components/ui/sidebar/nav-user";
import { DocumentSwitcher } from "@/components/ui/sidebar/document-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail
} from "@/components/ui/sidebar";

import NavChatUtils from "./nav-chat-utils";

// This is sample data.
const data = {
  user: {
    name: "Dexter Morgan",
    email: "itsover@example.com",
    avatar:
      "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOa6dHAJX491aFfndYY5Hl19JiWwGiG9w1Pw&s"
  },
  previousChatsList: [
    {
      id: "1",
      name: "Customer Support Inquiry - Billing Issues",
      date: new Date(2025, 1, 2)
    }, // 02-02-2025
    {
      id: "2",
      name: "Project Kickoff Meeting - Q1 Marketing Strategy",
      date: new Date(2025, 1, 1)
    }, // 01-02-2025
    {
      id: "3",
      name: "Brainstorming Session - New Product Features Discussion",
      date: new Date(2025, 0, 31)
    }, // 31-01-2025
    {
      id: "4",
      name: "Weekly Standup - Engineering Team Updates & Goals",
      date: new Date(2025, 0, 30)
    }, // 30-01-2025
    {
      id: "5",
      name: "Research & Development - AI-powered Chatbot Enhancements",
      date: new Date(2025, 0, 29)
    }, // 29-01-2025
    {
      id: "6",
      name: "User Feedback Review - Improving App Usability & UX",
      date: new Date(2025, 0, 28)
    }, // 28-01-2025
    {
      id: "7",
      name: "Company All-Hands Meeting - Key Announcements & Q&A",
      date: new Date(2025, 0, 27)
    }, // 27-01-2025
    {
      id: "8",
      name: "Partnership Negotiation - Collaboration Opportunities",
      date: new Date(2025, 0, 26)
    }, // 26-01-2025
    {
      id: "9",
      name: "Investor Pitch Discussion - Business Growth Strategies",
      date: new Date(2025, 0, 25)
    }, // 25-01-2025
    {
      id: "10",
      name: "Tech Support Follow-Up - Bug Fixes & Feature Requests",
      date: new Date(2025, 0, 24)
    }, // 24-01-2025
    {
      id: "11",
      name: "Marketing Campaign Strategy - Social Media Growth",
      date: new Date(2025, 0, 23)
    }, // 23-01-2025
    {
      id: "12",
      name: "Product Demo Feedback - Beta Testing Insights",
      date: new Date(2025, 0, 22)
    }, // 22-01-2025
    {
      id: "13",
      name: "Client Onboarding - Setup & Initial Walkthrough",
      date: new Date(2025, 0, 21)
    }, // 21-01-2025
    {
      id: "14",
      name: "Competitive Analysis - Industry Trends Review",
      date: new Date(2025, 0, 20)
    }, // 20-01-2025
    {
      id: "15",
      name: "Legal Consultation - Contract Review & Updates",
      date: new Date(2025, 0, 19)
    }, // 19-01-2025
    {
      id: "16",
      name: "Sales Pipeline Discussion - Lead Conversion Tactics",
      date: new Date(2025, 0, 18)
    }, // 18-01-2025
    {
      id: "17",
      name: "Internal Training Session - New Software Rollout",
      date: new Date(2025, 0, 17)
    }, // 17-01-2025
    {
      id: "18",
      name: "User Experience Testing - Design Feedback Review",
      date: new Date(2025, 0, 16)
    }, // 16-01-2025
    {
      id: "19",
      name: "Budget Planning Meeting - Fiscal Year Projections",
      date: new Date(2025, 0, 15)
    }, // 15-01-2025
    {
      id: "20",
      name: "Security & Compliance Audit - Risk Assessment",
      date: new Date(2025, 0, 14)
    } // 14-01-2025
  ]
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <DocumentSwitcher />
      </SidebarHeader>

      <SidebarContent>
        <NavChatUtils />
        <NavPreviousChatsList previousChatListProps={data.previousChatsList} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
