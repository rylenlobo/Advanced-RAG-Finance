import { create } from "zustand";

interface ModalState {
  isUploadDialogOpen: boolean;
  openUploadDialog: () => void;
  closeUploadDialog: () => void;
  toggleUploadDialog: () => void;
}

const useModalStore = create<ModalState>((set) => ({
  isUploadDialogOpen: false,

  openUploadDialog: () => set({ isUploadDialogOpen: true }),
  closeUploadDialog: () => set({ isUploadDialogOpen: false }),
  toggleUploadDialog: () =>
    set((state) => ({ isUploadDialogOpen: !state.isUploadDialogOpen }))
}));

export default useModalStore;
