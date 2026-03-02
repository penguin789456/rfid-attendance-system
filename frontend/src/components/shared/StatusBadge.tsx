import { Badge } from "@/components/ui/badge";
import { CHECK_IN_STATUS, CHECK_OUT_STATUS } from "@/lib/constants";

interface StatusBadgeProps {
  type: "checkIn" | "checkOut";
  value: number;
}

export function StatusBadge({ type, value }: StatusBadgeProps) {
  const map = type === "checkIn" ? CHECK_IN_STATUS : CHECK_OUT_STATUS;
  const status = map[value] ?? { label: "未知", variant: "secondary" as const };
  return <Badge variant={status.variant}>{status.label}</Badge>;
}
