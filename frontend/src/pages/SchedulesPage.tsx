import { useEffect, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Plus } from "lucide-react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DataTable } from "@/components/shared/DataTable";
import { FormDialog } from "@/components/shared/FormDialog";
import { DeleteConfirmDialog } from "@/components/shared/DeleteConfirmDialog";
import { PageHeader } from "@/components/shared/PageHeader";

import { useScheduleStore } from "@/stores/scheduleStore";
import { useDepartmentStore } from "@/stores/departmentStore";
import { useFlexSettingStore } from "@/stores/flexSettingStore";
import type { Schedule } from "@/types/schedule";
import { scheduleFormSchema, type ScheduleFormValues } from "@/types/schedule";
import { ACTIVE_DAY_LABELS, ACTIVE_DAY_OPTIONS, formatTime } from "@/lib/constants";

const NONE_VALUE = "__none__";

export function SchedulesPage() {
  const {
    schedules,
    isLoading,
    fetchSchedules,
    createSchedule,
    updateSchedule,
    deleteSchedule,
  } = useScheduleStore();
  const { departments, fetchDepartments } = useDepartmentStore();
  const { flexSettings, fetchFlexSettings } = useFlexSettingStore();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editing, setEditing] = useState<Schedule | null>(null);
  const [deleting, setDeleting] = useState<Schedule | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<ScheduleFormValues>({
    resolver: zodResolver(scheduleFormSchema),
    defaultValues: {
      Dept_GUID: "",
      Name: "",
      ActiveDay: 8,
      CheckInNeedBefore: "09:00",
      CheckNeedOutAfter: "18:00",
      DayCutoff: "04:00",
      FlexSetting_GUID: null,
    },
  });

  useEffect(() => {
    fetchSchedules();
    fetchDepartments();
    fetchFlexSettings();
  }, [fetchSchedules, fetchDepartments, fetchFlexSettings]);

  const deptName = (guid: string) =>
    departments.find((d) => d.GUID === guid)?.DeptName ?? guid;

  const flexLabel = (guid: string | null) => {
    if (!guid) return "—";
    const fs = flexSettings.find((f) => f.GUID === guid);
    return fs ? `${fs.FlexMinutes} 分鐘` : guid;
  };

  const openCreate = () => {
    setEditing(null);
    form.reset({
      Dept_GUID: "",
      Name: "",
      ActiveDay: 8,
      CheckInNeedBefore: "09:00",
      CheckNeedOutAfter: "18:00",
      DayCutoff: "04:00",
      FlexSetting_GUID: null,
    });
    setIsFormOpen(true);
  };

  const openEdit = (sched: Schedule) => {
    setEditing(sched);
    form.reset({
      Dept_GUID: sched.Dept_GUID,
      Name: sched.Name,
      ActiveDay: sched.ActiveDay,
      CheckInNeedBefore: formatTime(sched.CheckInNeedBefore),
      CheckNeedOutAfter: formatTime(sched.CheckNeedOutAfter),
      DayCutoff: formatTime(sched.DayCutoff),
      FlexSetting_GUID: sched.FlexSetting_GUID,
    });
    setIsFormOpen(true);
  };

  const onSubmit = form.handleSubmit(async (data) => {
    setIsSubmitting(true);
    try {
      if (editing) {
        await updateSchedule(editing.GUID, data);
        toast.success("班表更新成功");
      } else {
        await createSchedule(data);
        toast.success("班表新增成功");
      }
      setIsFormOpen(false);
    } catch {
      toast.error("操作失敗");
    } finally {
      setIsSubmitting(false);
    }
  });

  const onDelete = async () => {
    if (!deleting) return;
    try {
      await deleteSchedule(deleting.GUID);
      toast.success("班表刪除成功");
      setDeleting(null);
    } catch {
      toast.error("刪除失敗");
    }
  };

  const columns: ColumnDef<Schedule>[] = [
    { accessorKey: "Name", header: "班表名稱" },
    {
      accessorKey: "Dept_GUID",
      header: "部門",
      cell: ({ row }) => deptName(row.original.Dept_GUID),
    },
    {
      accessorKey: "ActiveDay",
      header: "適用日",
      cell: ({ row }) =>
        ACTIVE_DAY_LABELS[row.original.ActiveDay] ?? row.original.ActiveDay,
    },
    {
      accessorKey: "CheckInNeedBefore",
      header: "上班時間",
      cell: ({ row }) => formatTime(row.original.CheckInNeedBefore),
    },
    {
      accessorKey: "CheckNeedOutAfter",
      header: "下班時間",
      cell: ({ row }) => formatTime(row.original.CheckNeedOutAfter),
    },
    {
      accessorKey: "DayCutoff",
      header: "日切點",
      cell: ({ row }) => formatTime(row.original.DayCutoff),
    },
    {
      accessorKey: "FlexSetting_GUID",
      header: "彈性設定",
      cell: ({ row }) => flexLabel(row.original.FlexSetting_GUID),
    },
    {
      id: "actions",
      header: "操作",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => openEdit(row.original)}>
              編輯
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive"
              onClick={() => setDeleting(row.original)}
            >
              刪除
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="班表設定"
        action={
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            新增班表
          </Button>
        }
      />

      <DataTable columns={columns} data={schedules} isLoading={isLoading} />

      <FormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        title={editing ? "編輯班表" : "新增班表"}
        onSubmit={onSubmit}
        isSubmitting={isSubmitting}
      >
        <div className="grid gap-2">
          <Label>部門</Label>
          <Controller
            control={form.control}
            name="Dept_GUID"
            render={({ field }) => (
              <Select onValueChange={field.onChange} value={field.value}>
                <SelectTrigger>
                  <SelectValue placeholder="請選擇部門" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((d) => (
                    <SelectItem key={d.GUID} value={d.GUID}>
                      {d.DeptName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>
        <div className="grid gap-2">
          <Label>班表名稱</Label>
          <Input {...form.register("Name")} />
        </div>
        <div className="grid gap-2">
          <Label>適用日</Label>
          <Controller
            control={form.control}
            name="ActiveDay"
            render={({ field }) => (
              <Select
                onValueChange={(v) => field.onChange(Number(v))}
                value={String(field.value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ACTIVE_DAY_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="grid gap-2">
            <Label>上班時間</Label>
            <Input type="time" {...form.register("CheckInNeedBefore")} />
          </div>
          <div className="grid gap-2">
            <Label>下班時間</Label>
            <Input type="time" {...form.register("CheckNeedOutAfter")} />
          </div>
          <div className="grid gap-2">
            <Label>日切點</Label>
            <Input type="time" {...form.register("DayCutoff")} />
          </div>
        </div>
        <div className="grid gap-2">
          <Label>彈性設定（選填）</Label>
          <Controller
            control={form.control}
            name="FlexSetting_GUID"
            render={({ field }) => (
              <Select
                onValueChange={(v) =>
                  field.onChange(v === NONE_VALUE ? null : v)
                }
                value={field.value ?? NONE_VALUE}
              >
                <SelectTrigger>
                  <SelectValue placeholder="無" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={NONE_VALUE}>無</SelectItem>
                  {flexSettings.map((fs) => (
                    <SelectItem key={fs.GUID} value={fs.GUID}>
                      {fs.FlexMinutes} 分鐘
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>
      </FormDialog>

      <DeleteConfirmDialog
        open={!!deleting}
        onOpenChange={(open) => !open && setDeleting(null)}
        onConfirm={onDelete}
        description={`確定要刪除班表「${deleting?.Name}」嗎？`}
      />
    </div>
  );
}
