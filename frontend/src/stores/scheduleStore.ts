import { create } from "zustand";
import { scheduleService } from "@/services/scheduleService";
import type { Schedule, ScheduleFormValues } from "@/types/schedule";

interface ScheduleState {
  schedules: Schedule[];
  isLoading: boolean;
  error: string | null;
  fetchSchedules: () => Promise<void>;
  createSchedule: (payload: ScheduleFormValues) => Promise<void>;
  updateSchedule: (
    guid: string,
    payload: Partial<ScheduleFormValues>,
  ) => Promise<void>;
  deleteSchedule: (guid: string) => Promise<void>;
}

export const useScheduleStore = create<ScheduleState>((set) => ({
  schedules: [],
  isLoading: false,
  error: null,

  fetchSchedules: async () => {
    set({ isLoading: true, error: null });
    try {
      const schedules = await scheduleService.getAll();
      set({ schedules, isLoading: false });
    } catch {
      set({ error: "載入班表資料失敗", isLoading: false });
    }
  },

  createSchedule: async (payload) => {
    await scheduleService.create(payload);
    const schedules = await scheduleService.getAll();
    set({ schedules });
  },

  updateSchedule: async (guid, payload) => {
    await scheduleService.update(guid, payload);
    const schedules = await scheduleService.getAll();
    set({ schedules });
  },

  deleteSchedule: async (guid) => {
    await scheduleService.delete(guid);
    const schedules = await scheduleService.getAll();
    set({ schedules });
  },
}));
