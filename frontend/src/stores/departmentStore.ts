import { create } from "zustand";
import { departmentService } from "@/services/departmentService";
import type { Department, DepartmentFormValues } from "@/types/department";

interface DepartmentState {
  departments: Department[];
  isLoading: boolean;
  error: string | null;
  fetchDepartments: () => Promise<void>;
  createDepartment: (payload: DepartmentFormValues) => Promise<void>;
  updateDepartment: (
    guid: string,
    payload: Partial<DepartmentFormValues>,
  ) => Promise<void>;
  deleteDepartment: (guid: string) => Promise<void>;
}

export const useDepartmentStore = create<DepartmentState>((set) => ({
  departments: [],
  isLoading: false,
  error: null,

  fetchDepartments: async () => {
    set({ isLoading: true, error: null });
    try {
      const departments = await departmentService.getAll();
      set({ departments, isLoading: false });
    } catch {
      set({ error: "載入部門資料失敗", isLoading: false });
    }
  },

  createDepartment: async (payload) => {
    await departmentService.create(payload);
    const departments = await departmentService.getAll();
    set({ departments });
  },

  updateDepartment: async (guid, payload) => {
    await departmentService.update(guid, payload);
    const departments = await departmentService.getAll();
    set({ departments });
  },

  deleteDepartment: async (guid) => {
    await departmentService.delete(guid);
    const departments = await departmentService.getAll();
    set({ departments });
  },
}));
