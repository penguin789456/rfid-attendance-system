import { useEffect, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Plus } from "lucide-react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
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

import { useEmployeeStore } from "@/stores/employeeStore";
import { useDepartmentStore } from "@/stores/departmentStore";
import type { Employee } from "@/types/employee";
import { employeeFormSchema, type EmployeeFormValues } from "@/types/employee";

export function EmployeesPage() {
  const {
    employees,
    isLoading,
    fetchEmployees,
    createEmployee,
    updateEmployee,
    deleteEmployee,
  } = useEmployeeStore();
  const { departments, fetchDepartments } = useDepartmentStore();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editing, setEditing] = useState<Employee | null>(null);
  const [deleting, setDeleting] = useState<Employee | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<EmployeeFormValues>({
    resolver: zodResolver(employeeFormSchema),
    defaultValues: {
      EmpCode: "",
      Name: "",
      Dept_GUID: "",
      Active: true,
      RFID_ID: null,
    },
  });

  useEffect(() => {
    fetchEmployees();
    fetchDepartments();
  }, [fetchEmployees, fetchDepartments]);

  const deptName = (guid: string) =>
    departments.find((d) => d.GUID === guid)?.DeptName ?? guid;

  const openCreate = () => {
    setEditing(null);
    form.reset({
      EmpCode: "",
      Name: "",
      Dept_GUID: "",
      Active: true,
      RFID_ID: null,
    });
    setIsFormOpen(true);
  };

  const openEdit = (emp: Employee) => {
    setEditing(emp);
    form.reset({
      EmpCode: emp.EmpCode,
      Name: emp.Name,
      Dept_GUID: emp.Dept_GUID,
      Active: emp.Active,
      RFID_ID: emp.RFID_ID,
    });
    setIsFormOpen(true);
  };

  const onSubmit = form.handleSubmit(async (data) => {
    setIsSubmitting(true);
    try {
      const payload = { ...data, RFID_ID: data.RFID_ID || null };
      if (editing) {
        await updateEmployee(editing.GUID, payload);
        toast.success("員工更新成功");
      } else {
        await createEmployee(payload);
        toast.success("員工新增成功");
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
      await deleteEmployee(deleting.GUID);
      toast.success("員工刪除成功");
      setDeleting(null);
    } catch {
      toast.error("刪除失敗");
    }
  };

  const columns: ColumnDef<Employee>[] = [
    { accessorKey: "EmpCode", header: "員工編號" },
    { accessorKey: "Name", header: "姓名" },
    { accessorKey: "RFID_ID", header: "RFID 卡號", cell: ({ row }) => row.original.RFID_ID ?? "—" },
    {
      accessorKey: "Dept_GUID",
      header: "部門",
      cell: ({ row }) => deptName(row.original.Dept_GUID),
    },
    {
      accessorKey: "Active",
      header: "狀態",
      cell: ({ row }) => (
        <Badge variant={row.original.Active ? "default" : "secondary"}>
          {row.original.Active ? "在職" : "離職"}
        </Badge>
      ),
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
        title="員工管理"
        action={
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            新增員工
          </Button>
        }
      />

      <DataTable columns={columns} data={employees} isLoading={isLoading} />

      <FormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        title={editing ? "編輯員工" : "新增員工"}
        onSubmit={onSubmit}
        isSubmitting={isSubmitting}
      >
        <div className="grid gap-2">
          <Label>員工編號</Label>
          <Input {...form.register("EmpCode")} />
          {form.formState.errors.EmpCode && (
            <p className="text-sm text-destructive">
              {form.formState.errors.EmpCode.message}
            </p>
          )}
        </div>
        <div className="grid gap-2">
          <Label>姓名</Label>
          <Input {...form.register("Name")} />
          {form.formState.errors.Name && (
            <p className="text-sm text-destructive">
              {form.formState.errors.Name.message}
            </p>
          )}
        </div>
        <div className="grid gap-2">
          <Label>RFID 卡號（選填）</Label>
          <Input {...form.register("RFID_ID")} />
        </div>
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
          {form.formState.errors.Dept_GUID && (
            <p className="text-sm text-destructive">
              {form.formState.errors.Dept_GUID.message}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Controller
            control={form.control}
            name="Active"
            render={({ field }) => (
              <Switch checked={field.value} onCheckedChange={field.onChange} />
            )}
          />
          <Label>在職</Label>
        </div>
      </FormDialog>

      <DeleteConfirmDialog
        open={!!deleting}
        onOpenChange={(open) => !open && setDeleting(null)}
        onConfirm={onDelete}
        description={`確定要刪除員工「${deleting?.Name}」嗎？`}
      />
    </div>
  );
}
