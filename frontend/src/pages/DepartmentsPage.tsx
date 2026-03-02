import { useEffect, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal, Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

import { useDepartmentStore } from "@/stores/departmentStore";
import type { Department } from "@/types/department";
import {
  departmentFormSchema,
  type DepartmentFormValues,
} from "@/types/department";
import { formatDateTime } from "@/lib/constants";

export function DepartmentsPage() {
  const {
    departments,
    isLoading,
    fetchDepartments,
    createDepartment,
    updateDepartment,
    deleteDepartment,
  } = useDepartmentStore();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editing, setEditing] = useState<Department | null>(null);
  const [deleting, setDeleting] = useState<Department | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<DepartmentFormValues>({
    resolver: zodResolver(departmentFormSchema),
    defaultValues: { DeptCode: "", DeptName: "" },
  });

  useEffect(() => {
    fetchDepartments();
  }, [fetchDepartments]);

  const openCreate = () => {
    setEditing(null);
    form.reset({ DeptCode: "", DeptName: "" });
    setIsFormOpen(true);
  };

  const openEdit = (dept: Department) => {
    setEditing(dept);
    form.reset({ DeptCode: dept.DeptCode, DeptName: dept.DeptName });
    setIsFormOpen(true);
  };

  const onSubmit = form.handleSubmit(async (data) => {
    setIsSubmitting(true);
    try {
      if (editing) {
        await updateDepartment(editing.GUID, data);
        toast.success("部門更新成功");
      } else {
        await createDepartment(data);
        toast.success("部門新增成功");
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
      await deleteDepartment(deleting.GUID);
      toast.success("部門刪除成功");
      setDeleting(null);
    } catch {
      toast.error("刪除失敗");
    }
  };

  const columns: ColumnDef<Department>[] = [
    { accessorKey: "DeptCode", header: "部門代碼" },
    { accessorKey: "DeptName", header: "部門名稱" },
    {
      accessorKey: "CreateTime",
      header: "建立時間",
      cell: ({ row }) => formatDateTime(row.getValue("CreateTime")),
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
        title="部門管理"
        action={
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            新增部門
          </Button>
        }
      />

      <DataTable columns={columns} data={departments} isLoading={isLoading} />

      <FormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        title={editing ? "編輯部門" : "新增部門"}
        onSubmit={onSubmit}
        isSubmitting={isSubmitting}
      >
        <div className="grid gap-2">
          <Label htmlFor="DeptCode">部門代碼</Label>
          <Input id="DeptCode" {...form.register("DeptCode")} />
          {form.formState.errors.DeptCode && (
            <p className="text-sm text-destructive">
              {form.formState.errors.DeptCode.message}
            </p>
          )}
        </div>
        <div className="grid gap-2">
          <Label htmlFor="DeptName">部門名稱</Label>
          <Input id="DeptName" {...form.register("DeptName")} />
          {form.formState.errors.DeptName && (
            <p className="text-sm text-destructive">
              {form.formState.errors.DeptName.message}
            </p>
          )}
        </div>
      </FormDialog>

      <DeleteConfirmDialog
        open={!!deleting}
        onOpenChange={(open) => !open && setDeleting(null)}
        onConfirm={onDelete}
        description={`確定要刪除部門「${deleting?.DeptName}」嗎？`}
      />
    </div>
  );
}
