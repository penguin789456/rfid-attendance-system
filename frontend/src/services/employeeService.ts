import api from "./api";
import type { Employee, EmployeeFormValues } from "@/types/employee";

export const employeeService = {
  getAll: async (
    skip = 0,
    limit = 100,
    activeOnly = false,
  ): Promise<Employee[]> => {
    const { data } = await api.get<Employee[]>("/employees", {
      params: { skip, limit, active_only: activeOnly },
    });
    return data;
  },

  getById: async (guid: string): Promise<Employee> => {
    const { data } = await api.get<Employee>(`/employees/${guid}`);
    return data;
  },

  create: async (payload: EmployeeFormValues): Promise<Employee> => {
    const { data } = await api.post<Employee>("/employees", payload);
    return data;
  },

  update: async (
    guid: string,
    payload: Partial<EmployeeFormValues>,
  ): Promise<Employee> => {
    const { data } = await api.put<Employee>(`/employees/${guid}`, payload);
    return data;
  },

  delete: async (guid: string): Promise<void> => {
    await api.delete(`/employees/${guid}`);
  },
};
