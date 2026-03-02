import { useEffect } from "react";
import type { ColumnDef } from "@tanstack/react-table";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DataTable } from "@/components/shared/DataTable";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { DatePicker } from "@/components/shared/DatePicker";

import { useAttendanceStore } from "@/stores/attendanceStore";
import type { AttendanceDaily } from "@/types/attendance";
import { formatDateTime } from "@/lib/constants";

export function AttendancePage() {
  const { records, isLoading, filters, setFilters, fetchAttendance } =
    useAttendanceStore();

  useEffect(() => {
    fetchAttendance();
  }, [fetchAttendance]);

  const columns: ColumnDef<AttendanceDaily>[] = [
    { accessorKey: "RFID_ID", header: "RFID 卡號" },
    { accessorKey: "WorkDate", header: "工作日" },
    {
      accessorKey: "FirstInTime",
      header: "首次打卡",
      cell: ({ row }) =>
        row.original.FirstInTime
          ? formatDateTime(row.original.FirstInTime)
          : "—",
    },
    {
      accessorKey: "LastOutTime",
      header: "最後打卡",
      cell: ({ row }) =>
        row.original.LastOutTime
          ? formatDateTime(row.original.LastOutTime)
          : "—",
    },
    {
      accessorKey: "CheckInStatus",
      header: "上班狀態",
      cell: ({ row }) => (
        <StatusBadge type="checkIn" value={row.original.CheckInStatus} />
      ),
    },
    {
      accessorKey: "CheckOutStatus",
      header: "下班狀態",
      cell: ({ row }) => (
        <StatusBadge type="checkOut" value={row.original.CheckOutStatus} />
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="出勤記錄" />

      <div className="flex items-center gap-4 mb-4">
        <DatePicker
          value={filters.work_date}
          onChange={(date) => setFilters({ work_date: date })}
          placeholder="選擇日期"
        />
        <Input
          className="w-[200px]"
          placeholder="RFID 卡號"
          value={filters.rfid_id ?? ""}
          onChange={(e) => setFilters({ rfid_id: e.target.value })}
        />
        <Button onClick={fetchAttendance}>查詢</Button>
      </div>

      <DataTable columns={columns} data={records} isLoading={isLoading} />
    </div>
  );
}
