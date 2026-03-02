import { z } from "zod";

export interface Employee {
  GUID: string;
  RFID_ID: string | null;
  EmpCode: string;
  Name: string;
  Dept_GUID: string;
  Active: boolean;
  CreateTime: string;
  UpdateTime: string;
}

export const employeeFormSchema = z.object({
  EmpCode: z.string().min(1, "員工編號為必填"),
  Name: z.string().min(1, "員工姓名為必填"),
  Dept_GUID: z.string().min(1, "請選擇部門"),
  Active: z.boolean().default(true),
  RFID_ID: z.string().nullable().optional(),
});

export type EmployeeFormValues = z.infer<typeof employeeFormSchema>;
