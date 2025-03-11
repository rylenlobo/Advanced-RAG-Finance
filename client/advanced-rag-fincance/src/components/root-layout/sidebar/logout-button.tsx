"use client";

import { supabase } from "@/utils/supabase/client/supabase-client";
import { DropdownMenuItem } from "../../ui/dropdown-menu";
import { LogOut } from "lucide-react";
import React from "react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

const LogoutButton = () => {
  const router = useRouter();

  async function logoutUser() {
    const {
      data: { user }
    } = await supabase.auth.getUser();

    if (user) {
      await supabase.auth.signOut();
      Cookies.remove("selectedDocumentDetails");
    }

    toast.success("Logged Out Succesfully");
    router.push("/login");
  }

  return (
    <DropdownMenuItem onClick={logoutUser}>
      <LogOut />
      Log out
    </DropdownMenuItem>
  );
};

export default LogoutButton;
