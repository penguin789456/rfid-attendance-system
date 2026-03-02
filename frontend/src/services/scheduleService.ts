import api from "./api";
import type { Schedule, ScheduleFormValues } from "@/types/schedule";
import { timeForApi } from "@/lib/constants";

export const scheduleService = {
  getAll: async (
    skip = 0,
    limit = 100,
    includeDeleted = false,
  ): Promise<Schedule[]> => {
    const { data } = await api.get<Schedule[]>("/schedules", {
      params: { skip, limit, include_deleted: includeDeleted },
    });
    return data;
  },

  getById: async (guid: string): Promise<Schedule> => {
    const { data } = await api.get<Schedule>(`/schedules/${guid}`);
    return data;
  },

  create: async (payload: ScheduleFormValues): Promise<Schedule> => {
    const body = {
      ...payload,
      CheckInNeedBefore: timeForApi(payload.CheckInNeedBefore),
      CheckNeedOutAfter: timeForApi(payload.CheckNeedOutAfter),
      DayCutoff: timeForApi(payload.DayCutoff),
      FlexSetting_GUID: payload.FlexSetting_GUID || null,
    };
    const { data } = await api.post<Schedule>("/schedules", body);
    return data;
  },

  update: async (
    guid: string,
    payload: Partial<ScheduleFormValues>,
  ): Promise<Schedule> => {
    const body = { ...payload } as Record<string, unknown>;
    if (payload.CheckInNeedBefore)
      body.CheckInNeedBefore = timeForApi(payload.CheckInNeedBefore);
    if (payload.CheckNeedOutAfter)
      body.CheckNeedOutAfter = timeForApi(payload.CheckNeedOutAfter);
    if (payload.DayCutoff) body.DayCutoff = timeForApi(payload.DayCutoff);
    if ("FlexSetting_GUID" in payload)
      body.FlexSetting_GUID = payload.FlexSetting_GUID || null;
    const { data } = await api.put<Schedule>(`/schedules/${guid}`, body);
    return data;
  },

  delete: async (guid: string, deletedBy = "ADMIN"): Promise<void> => {
    await api.delete(`/schedules/${guid}`, {
      params: { deleted_by: deletedBy },
    });
  },
};
