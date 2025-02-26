import { create } from "zustand";
import Cookies from "js-cookie";
import type { Document } from "@/network/fetch-documents";

interface DocumentStore {
  selectedDocumentDetails: Document | null;
  setSelectedDocument: (document: Document) => void;
  clearSelectedDocument: () => void;
}

const useDocumentStore = create<DocumentStore>((set) => ({
  selectedDocumentDetails: JSON.parse(
    Cookies.get("selectedDocumentDetails") || "null"
  ),

  setSelectedDocument: (document) => {
    Cookies.set("selectedDocumentDetails", JSON.stringify(document), {
      expires: 7
    }); // Expires in 7 days
    set({ selectedDocumentDetails: document });
  },

  clearSelectedDocument: () => {
    Cookies.remove("selectedDocumentDetails");
    set({ selectedDocumentDetails: null });
  }
}));

export default useDocumentStore;
