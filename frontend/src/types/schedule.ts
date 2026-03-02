import { z } from "zod";

export interface Schedule {
  GUID: string;
  Dept_GUID: string;
  Name: string;
  ActiveDay: number;
  CheckInNeedBefore: string;
  CheckNeedOutAfter: string;
  DayCutoff: string;
  FlexSetting_GUID: string | null;
  IsDeleted: boolean;
  DeletedTime: string | null;
  DeletedBy: string | null;
  CreateTime: string;
  UpdateTime: string;
}

export const scheduleFormSchema = z.object({
  Dept_GUID: z.string().min(1, "請選擇部門"),
  Name: z.string().min(1, "班表名稱為必填"),
  ActiveDay: z.coerce.number().min(1).max(8),
  CheckInNeedBefore: z.string().min(1, "上班時間為必填"),
  CheckNeedOutAfter: z.string().min(1, "下班時間為必填"),
  DayCutoff: z.string().min(1, "日切點為必填"),
  FlexSetting_GUID: z.string().nullable().optional(),
});

export type ScheduleFormValues = z.infer<typeof scheduleFormSchema>;
