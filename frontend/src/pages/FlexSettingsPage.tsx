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

import { useFlexSettingStore } from "@/stores/flexSettingStore";
import type { FlexSetting } from "@/types/flexSetting";
import {
  flexSettingFormSchema,
  type FlexSettingFormValues,
} from "@/types/flexSetting";
import { formatDateTime } from "@/lib/constants";

export function FlexSettingsPage() {
  const {
    flexSettings,
    isLoading,
    fetchFlexSettings,
    createFlexSetting,
    updateFlexSetting,
    deleteFlexSetting,
  } = useFlexSettingStore();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editing, setEditing] = useState<FlexSetting | null>(null);
  const [deleting, setDeleting] = useState<FlexSetting | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<FlexSettingFormValues>({
    resolver: zodResolver(flexSettingFormSchema),
    defaultValues: { FlexMinutes: 0 },
  });

  useEffect(() => {
    fetchFlexSettings();
  }, [fetchFlexSettings]);

  const openCreate = () => {
    setEditing(null);
    form.reset({ FlexMinutes: 0 });
    setIsFormOpen(true);
  };

  const openEdit = (item: FlexSetting) => {
    setEditing(item);
    form.reset({ FlexMinutes: item.FlexMinutes });
    setIsFormOpen(true);
  };

  const onSubmit = form.handleSubmit(async (data) => {
    setIsSubmitting(true);
    try {
      if (editing) {
        await updateFlexSetting(editing.GUID, data);
        toast.success("彈性設定更新成功");
      } else {
        await createFlexSetting(data);
        toast.success("彈性設定新增成功");
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
      await deleteFlexSetting(deleting.GUID);
      toast.success("彈性設定刪除成功");
      setDeleting(null);
    } catch {
      toast.error("刪除失敗");
    }
  };

  const columns: ColumnDef<FlexSetting>[] = [
    {
      accessorKey: "GUID",
      header: "ID",
      cell: ({ row }) => row.original.GUID.slice(0, 8) + "...",
    },
    { accessorKey: "FlexMinutes", header: "彈性分鐘數" },
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
        title="彈性設定"
        action={
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            新增彈性設定
          </Button>
        }
      />

      <DataTable columns={columns} data={flexSettings} isLoading={isLoading} />

      <FormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        title={editing ? "編輯彈性設定" : "新增彈性設定"}
        onSubmit={onSubmit}
        isSubmitting={isSubmitting}
      >
        <div className="grid gap-2">
          <Label htmlFor="FlexMinutes">彈性分鐘數</Label>
          <Input
            id="FlexMinutes"
            type="number"
            min={0}
            {...form.register("FlexMinutes")}
          />
          {form.formState.errors.FlexMinutes && (
            <p className="text-sm text-destructive">
              {form.formState.errors.FlexMinutes.message}
            </p>
          )}
        </div>
      </FormDialog>

      <DeleteConfirmDialog
        open={!!deleting}
        onOpenChange={(open) => !open && setDeleting(null)}
        onConfirm={onDelete}
        description={`確定要刪除彈性設定（${deleting?.FlexMinutes} 分鐘）嗎？`}
      />
    </div>
  );
}
