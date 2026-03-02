import api from "./api";
import type { FlexSetting, FlexSettingFormValues } from "@/types/flexSetting";

export const flexSettingService = {
  getAll: async (
    skip = 0,
    limit = 100,
    includeDeleted = false,
  ): Promise<FlexSetting[]> => {
    const { data } = await api.get<FlexSetting[]>("/flex-settings", {
      params: { skip, limit, include_deleted: includeDeleted },
    });
    return data;
  },

  getById: async (guid: string): Promise<FlexSetting> => {
    const { data } = await api.get<FlexSetting>(`/flex-settings/${guid}`);
    return data;
  },

  create: async (payload: FlexSettingFormValues): Promise<FlexSetting> => {
    const { data } = await api.post<FlexSetting>("/flex-settings", payload);
    return data;
  },

  update: async (
    guid: string,
    payload: Partial<FlexSettingFormValues>,
  ): Promise<FlexSetting> => {
    const { data } = await api.put<FlexSetting>(
      `/flex-settings/${guid}`,
      payload,
    );
    return data;
  },

  delete: async (guid: string, deletedBy = "ADMIN"): Promise<void> => {
    await api.delete(`/flex-settings/${guid}`, {
      params: { deleted_by: deletedBy },
    });
  },
};
