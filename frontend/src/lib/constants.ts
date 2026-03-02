export const ACTIVE_DAY_LABELS: Record<number, string> = {
  1: "週一",
  2: "週二",
  3: "週三",
  4: "週四",
  5: "週五",
  6: "週六",
  7: "週日",
  8: "全年",
};

export const ACTIVE_DAY_OPTIONS = [
  { value: "1", label: "週一" },
  { value: "2", label: "週二" },
  { value: "3", label: "週三" },
  { value: "4", label: "週四" },
  { value: "5", label: "週五" },
  { value: "6", label: "週六" },
  { value: "7", label: "週日" },
  { value: "8", label: "全年" },
];

export const CHECK_IN_STATUS: Record<
  number,
  { label: string; variant: "default" | "secondary" | "destructive" }
> = {
  0: { label: "正常", variant: "default" },
  1: { label: "彈性", variant: "secondary" },
  2: { label: "遲到", variant: "destructive" },
};

export const CHECK_OUT_STATUS: Record<
  number,
  { label: string; variant: "default" | "secondary" | "destructive" }
> = {
  0: { label: "正常", variant: "default" },
  1: { label: "早退", variant: "secondary" },
  2: { label: "缺卡", variant: "destructive" },
};

export function formatDateTime(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleString("zh-TW");
}

export function formatTime(time: string): string {
  if (!time) return "";
  return time.slice(0, 5);
}

export function timeForApi(time: string): string {
  if (time.length === 5) return time + ":00";
  return time;
}
