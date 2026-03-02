import api from "./api";
import type { AttendanceDaily } from "@/types/attendance";

export const attendanceService = {
  getAll: async (
    skip = 0,
    limit = 100,
    workDate?: string,
    rfidId?: string,
  ): Promise<AttendanceDaily[]> => {
    const params: Record<string, unknown> = { skip, limit };
    if (workDate) params.work_date = workDate;
    if (rfidId) params.rfid_id = rfidId;
    const { data } = await api.get<AttendanceDaily[]>("/attendance-daily", {
      params,
    });
    return data;
  },

  getById: async (guid: string): Promise<AttendanceDaily> => {
    const { data } = await api.get<AttendanceDaily>(
      `/attendance-daily/${guid}`,
    );
    return data;
  },
};
