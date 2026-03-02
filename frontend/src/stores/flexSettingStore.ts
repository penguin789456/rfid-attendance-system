import { create } from "zustand";
import { flexSettingService } from "@/services/flexSettingService";
import type { FlexSetting, FlexSettingFormValues } from "@/types/flexSetting";

interface FlexSettingState {
  flexSettings: FlexSetting[];
  isLoading: boolean;
  error: string | null;
  fetchFlexSettings: () => Promise<void>;
  createFlexSetting: (payload: FlexSettingFormValues) => Promise<void>;
  updateFlexSetting: (
    guid: string,
    payload: Partial<FlexSettingFormValues>,
  ) => Promise<void>;
  deleteFlexSetting: (guid: string) => Promise<void>;
}

export const useFlexSettingStore = create<FlexSettingState>((set) => ({
  flexSettings: [],
  isLoading: false,
  error: null,

  fetchFlexSettings: async () => {
    set({ isLoading: true, error: null });
    try {
      const flexSettings = await flexSettingService.getAll();
      set({ flexSettings, isLoading: false });
    } catch {
      set({ error: "載入彈性設定失敗", isLoading: false });
    }
  },

  createFlexSetting: async (payload) => {
    await flexSettingService.create(payload);
    const flexSettings = await flexSettingService.getAll();
    set({ flexSettings });
  },

  updateFlexSetting: async (guid, payload) => {
    await flexSettingService.update(guid, payload);
    const flexSettings = await flexSettingService.getAll();
    set({ flexSettings });
  },

  deleteFlexSetting: async (guid) => {
    await flexSettingService.delete(guid);
    const flexSettings = await flexSettingService.getAll();
    set({ flexSettings });
  },
}));
