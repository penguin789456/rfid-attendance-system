import { create } from "zustand";
import { attendanceService } from "@/services/attendanceService";
import type { AttendanceDaily, AttendanceFilters } from "@/types/attendance";

interface AttendanceState {
  records: AttendanceDaily[];
  isLoading: boolean;
  error: string | null;
  filters: AttendanceFilters;
  setFilters: (filters: Partial<AttendanceFilters>) => void;
  fetchAttendance: () => Promise<void>;
}

export const useAttendanceStore = create<AttendanceState>((set, get) => ({
  records: [],
  isLoading: false,
  error: null,
  filters: {},

  setFilters: (filters) => {
    set((state) => ({ filters: { ...state.filters, ...filters } }));
  },

  fetchAttendance: async () => {
    set({ isLoading: true, error: null });
    try {
      const { filters } = get();
      const records = await attendanceService.getAll(
        0,
        100,
        filters.work_date,
        filters.rfid_id,
      );
      set({ records, isLoading: false });
    } catch {
      set({ error: "載入考勤資料失敗", isLoading: false });
    }
  },
}));
