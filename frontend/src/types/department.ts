import { z } from "zod";

export interface Department {
  GUID: string;
  DeptCode: string;
  DeptName: string;
  CreateTime: string;
  UpdateTime: string;
}

export const departmentFormSchema = z.object({
  DeptCode: z.string().min(1, "部門代碼為必填"),
  DeptName: z.string().min(1, "部門名稱為必填"),
});

export type DepartmentFormValues = z.infer<typeof departmentFormSchema>;
