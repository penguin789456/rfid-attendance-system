import { create } from "zustand";
import { employeeService } from "@/services/employeeService";
import type { Employee, EmployeeFormValues } from "@/types/employee";

interface EmployeeState {
  employees: Employee[];
  isLoading: boolean;
  error: string | null;
  fetchEmployees: (activeOnly?: boolean) => Promise<void>;
  createEmployee: (payload: EmployeeFormValues) => Promise<void>;
  updateEmployee: (
    guid: string,
    payload: Partial<EmployeeFormValues>,
  ) => Promise<void>;
  deleteEmployee: (guid: string) => Promise<void>;
}

export const useEmployeeStore = create<EmployeeState>((set) => ({
  employees: [],
  isLoading: false,
  error: null,

  fetchEmployees: async (activeOnly = false) => {
    set({ isLoading: true, error: null });
    try {
      const employees = await employeeService.getAll(0, 100, activeOnly);
      set({ employees, isLoading: false });
    } catch {
      set({ error: "載入員工資料失敗", isLoading: false });
    }
  },

  createEmployee: async (payload) => {
    await employeeService.create(payload);
    const employees = await employeeService.getAll();
    set({ employees });
  },

  updateEmployee: async (guid, payload) => {
    await employeeService.update(guid, payload);
    const employees = await employeeService.getAll();
    set({ employees });
  },

  deleteEmployee: async (guid) => {
    await employeeService.delete(guid);
    const employees = await employeeService.getAll();
    set({ employees });
  },
}));
