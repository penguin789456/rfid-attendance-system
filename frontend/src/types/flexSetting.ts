import { z } from "zod";

export interface FlexSetting {
  GUID: string;
  FlexMinutes: number;
  IsDeleted: boolean;
  DeletedTime: string | null;
  DeletedBy: string | null;
  CreateTime: string;
  UpdateTime: string;
}

export const flexSettingFormSchema = z.object({
  FlexMinutes: z.coerce.number().min(0, "彈性分鐘數不可為負數"),
});

export type FlexSettingFormValues = z.infer<typeof flexSettingFormSchema>;
