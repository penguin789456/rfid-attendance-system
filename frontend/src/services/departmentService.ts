import api from "./api";
import type { Department, DepartmentFormValues } from "@/types/department";

export const departmentService = {
  getAll: async (skip = 0, limit = 100): Promise<Department[]> => {
    const { data } = await api.get<Department[]>("/departments", {
      params: { skip, limit },
    });
    return data;
  },

  getById: async (guid: string): Promise<Department> => {
    const { data } = await api.get<Department>(`/departments/${guid}`);
    return data;
  },

  create: async (payload: DepartmentFormValues): Promise<Department> => {
    const { data } = await api.post<Department>("/departments", payload);
    return data;
  },

  update: async (
    guid: string,
    payload: Partial<DepartmentFormValues>,
  ): Promise<Department> => {
    const { data } = await api.put<Department>(
      `/departments/${guid}`,
      payload,
    );
    return data;
  },

  delete: async (guid: string): Promise<void> => {
    await api.delete(`/departments/${guid}`);
  },
};
