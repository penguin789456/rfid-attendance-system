export interface AttendanceDaily {
  GUID: string;
  RFID_ID: string;
  WorkDate: string;
  RequiredConfigGUID: string | null;
  FirstInTime: string | null;
  LastOutTime: string | null;
  CheckInStatus: number;
  CheckOutStatus: number;
  ExceptionFlags: string | null;
  CreateTime: string;
  UpdateTime: string;
}

export interface AttendanceFilters {
  work_date?: string;
  rfid_id?: string;
}
