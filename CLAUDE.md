# CLAUDE.md

本檔案為 Claude Code (claude.ai/code) 在此程式庫中工作時提供指導。

## 專案概述

這是一個**企業級 RFID 出勤系統**，專為使用 RFID 卡追蹤員工出勤而設計。系統建立在不可變性、出勤規則版本控制和部門級別配置的核心原則上。

## 核心架構原則

### 1. RFID 作為單一事實來源
- RFID 卡刷卡是上下班打卡的唯一方法
- 所有出勤事件都源自 `ScanEvents` 表

### 2. 部門級別規則管理
- 每個部門都有自己的班表（`Schedules` 表）和彈性設定（`FlexSettings` 表）
- 規則透過 `RequiredConfigs` 表進行版本控制（不可變快照）

### 3. 規則鎖定邏輯（關鍵）
- **當員工在某天首次打卡上班時，該員工整個工作日的 `RequiredConfig` 就會被鎖定**
- HR 對班表/彈性設定的更新只會影響尚未打卡的員工
- 這可防止追溯性規則變更影響已開始的工作日

### 4. 不儲存衍生資料
- 不要儲存計算值如「CalcOutTime」
- 只儲存最終狀態列舉（`CheckInStatus`、`CheckOutStatus`）

## 資料庫架構

### 核心表結構
```
Departments（部門）
 ├─ Employees（員工）
 │   ├─ ScanEvents（原始 RFID 刷卡事件）
 │   └─ AttendanceDaily ── RequiredConfigs ── Schedules
 │                                      └─ FlexSettings
```

### 主要資料表

**Schedules（班表）**（`Dept_GUID, ActiveDay` 在 `IsDeleted=0` 時唯一）
- 啟用軟刪除
- `ActiveDay`：1-7（週一至週日），8=全年
- `DayCutoff`：日期分界時間（例如 04:00）

**FlexSettings（彈性設定）**（`Dept_GUID` 在 `IsDeleted=0` 時唯一）
- 啟用軟刪除
- 部門級別的彈性時間（分鐘）

**RequiredConfigs（規則配置快照）**（不可變）
- 當 HR 發布 Schedules 或 FlexSettings 時建立
- 包含凍結的副本：`RequiredIn`、`RequiredOut`、`FlexMinutes`、`DayCutoff`
- `EffectiveTo`：NULL 表示仍然有效

**AttendanceDaily（每日出勤）**
- 每位員工每個工作日一筆記錄
- `RequiredConfigGUID`：連結到使用的規則版本（在首次打卡時設定）
- 狀態欄位使用列舉（見下方）

### 狀態列舉

**CheckInStatus（上班打卡狀態）**
- 0 = NORMAL（正常）
- 1 = FLEX（在彈性時間內）
- 2 = LATE（遲到）

**CheckOutStatus（下班打卡狀態）**
- 0 = NORMAL（正常）
- 1 = EARLY（早退）
- 2 = MISSING（缺卡）

## 上下班打卡流程（POST /api/scan）

1. 從 RFID 讀卡機接收 `rfid_id`
2. 透過 `Employees` 表驗證員工並取得 `Dept_GUID`
3. 查詢有效的 `Schedules`（按 `ActiveDay`、`IsDeleted=0`）和 `FlexSettings`（按部門）
4. 使用班表中的 `DayCutoff` 來判定 `WorkDate`
5. 插入到 `ScanEvents`
6. **Upsert** `AttendanceDaily (RFID_ID, WorkDate)`：
   - **如果是當天首次打卡**：將 `RequiredConfigGUID` 設為當前有效版本
   - **如果已存在**：更新 `FirstInTime` 或 `LastOutTime`（不要更改 `RequiredConfigGUID`）
7. 使用鎖定的 `RequiredConfig` 計算狀態
8. 更新 `CheckInStatus` 和 `CheckOutStatus`

## 日期分界邏輯

`DayCutoff` 欄位決定刷卡屬於哪個日曆日：
- 分界時間之前的刷卡屬於前一個日曆日
- 範例：當 `DayCutoff=04:00` 時，1月2日 02:30 的刷卡屬於1月1日的工作日

## 開發指南

### 實作 API 端點時
- 始終驗證 `RFID_ID` 存在於 `Employees` 表中且 `Active=1`
- 更新多個表時使用交易（例如 `ScanEvents` + `AttendanceDaily`）
- 建立後永不修改 `RequiredConfigs`
- 查詢 `Schedules` 或 `FlexSettings` 時檢查 `IsDeleted=0`

### 實作 HR 管理功能時
- 僅使用軟刪除：設定 `IsDeleted=1`、`DeletedTime`、`DeletedBy`
- 發布新規則時，建立新的 `RequiredConfig` 記錄
- 替換時在舊的 `RequiredConfig` 記錄上設定 `EffectiveTo`

### 需強制執行的資料庫約束
- 唯一約束：`Schedules` 中 `IsDeleted=0` 時的 `(Dept_GUID, ActiveDay)`
- 唯一約束：`FlexSettings` 中 `IsDeleted=0` 時的 `Dept_GUID`
- 所有 GUID 參照的外鍵完整性

## 技術背景

根據程式庫路徑，這似乎是為 Arduino/嵌入式實作設計的。請考慮：
- 資料庫可能是 SQLite 或類似的嵌入式資料庫
- RFID 讀卡機透過 UART/SPI/I2C 整合
- 即時時鐘（RTC）模組以獲得準確的時間戳記
- 可能使用 LCD/OLED 顯示器提供使用者回饋

---

## 開發環境與技術棧

### 後端技術選擇
- **框架**：Python 3.11+ / FastAPI
- **資料庫**：SQLite（開發）/ PostgreSQL（生產）
- **ORM**：SQLAlchemy 2.0+
- **驗證**：Pydantic v2
- **非同步**：asyncio + aiosqlite
- **Linter/Formatter**：Ruff

### Ruff 配置
在 `pyproject.toml` 中配置：
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.ruff.format]
quote-style = "double"
```

### Python 編碼規範
- 使用 Ruff 進行程式碼檢查和格式化
- 使用 Type Hints 進行型別標註
- 函數命名使用 snake_case
- 類別命名使用 PascalCase
- 常數使用 UPPER_SNAKE_CASE
- 使用 async/await 處理 I/O 操作
- 每個函數/方法需有 docstring

### 後端專案結構
```
backend/
├── app/
│   ├── main.py              # FastAPI 應用入口
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API 路由
│   ├── services/            # 業務邏輯
│   ├── repositories/        # 資料存取層
│   └── utils/               # 工具函數
├── tests/                   # 測試檔案
├── alembic/                 # 資料庫遷移
├── pyproject.toml           # 專案配置（含 Ruff）
└── requirements.txt
```

---

## 前端架構規範

### 前端技術選擇
- **框架**：React 18+ / Next.js 14+（App Router）
- **UI 元件庫**：Shadcn/ui + Tailwind CSS
- **狀態管理**：Zustand
- **HTTP 客戶端**：Axios 或 fetch
- **表單處理**：React Hook Form + Zod

### TypeScript 編碼規範
- 嚴格模式（strict: true）
- 介面使用 `I` 前綴或直接使用描述性名稱
- 型別定義使用 PascalCase
- 函數和變數使用 camelCase
- 元件檔案使用 PascalCase：`EmployeeList.tsx`
- 工具函數檔案使用 camelCase：`formatDate.ts`

### 前端專案結構
```
frontend/
├── src/
│   ├── app/                 # Next.js App Router 頁面
│   │   ├── (dashboard)/     # 儀表板路由群組
│   │   ├── api/             # API 路由（如需要）
│   │   ├── layout.tsx       # 根佈局
│   │   └── page.tsx         # 首頁
│   ├── components/
│   │   ├── ui/              # Shadcn/ui 元件
│   │   └── features/        # 功能元件
│   ├── hooks/               # 自訂 Hooks
│   ├── lib/                 # 工具函數
│   ├── stores/              # Zustand stores
│   ├── types/               # TypeScript 型別定義
│   └── services/            # API 服務層
├── public/                  # 靜態資源
└── package.json
```

### 元件設計原則
- 優先使用 Server Components
- 需要互動時標記 "use client"
- 保持元件單一職責
- Props 使用解構賦值
- 避免過深的元件巢狀（最多 3-4 層）

### Zustand Store 規範
```typescript
// stores/employeeStore.ts
import { create } from 'zustand'

interface EmployeeState {
  employees: Employee[]
  isLoading: boolean
  fetchEmployees: () => Promise<void>
}

export const useEmployeeStore = create<EmployeeState>((set) => ({
  employees: [],
  isLoading: false,
  fetchEmployees: async () => {
    set({ isLoading: true })
    // API 呼叫
    set({ employees: data, isLoading: false })
  }
}))
```

---

## 資料庫規範

### 命名原則
- 資料表：**複數名詞** PascalCase
- 欄位：**PascalCase**
- 主鍵：`GUID` 或 `{Entity}_ID`
- 外鍵：`{RelatedTable}_GUID`
- 布林欄位：`Is{State}` 或 `Has{Feature}`
- 時間欄位：`{Action}Time`

### 索引命名
- 主鍵：`PK_{TableName}`
- 外鍵：`FK_{TableName}_{ColumnName}`
- 唯一索引：`UQ_{TableName}_{ColumnName}`
- 一般索引：`IX_{TableName}_{ColumnName}`

### 完整資料表定義

#### Departments（部門）
| 欄位 | 型別 | 說明 |
|------|------|------|
| GUID | TEXT (PK) | 部門唯一識別 |
| DeptCode | TEXT | 部門代碼 |
| DeptName | TEXT | 部門名稱 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

#### Employees（員工）
| 欄位 | 型別 | 說明 |
|------|------|------|
| RFID_ID | TEXT (PK) | RFID 卡 GUID |
| EmpCode | TEXT | 員工編號 |
| Name | TEXT | 員工姓名 |
| Dept_GUID | TEXT (FK) | 所屬部門 |
| Active | BOOLEAN | 是否在職 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

#### Schedules（部門班表，軟刪除）
> 唯一約束：`(Dept_GUID, ActiveDay)` 在 `IsDeleted = 0` 下唯一

| 欄位 | 型別 | 說明 |
|------|------|------|
| GUID | TEXT (PK) | 班表 ID |
| Dept_GUID | TEXT (FK) | 部門 |
| Name | TEXT | 班表名稱 |
| ActiveDay | INTEGER | 1–7（週一至週日），8=全年 |
| CheckInNeedBefore | TIME | 規定上班時間 |
| CheckNeedOutAfter | TIME | 規定下班時間 |
| DayCutoff | TIME | 日切點（如 04:00） |
| IsDeleted | BOOLEAN | 軟刪除 |
| DeletedTime | DATETIME | 刪除時間 |
| DeletedBy | TEXT | 刪除人 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

#### FlexSettings（彈性設定，軟刪除）
> 唯一約束：`Dept_GUID` 在 `IsDeleted = 0` 下唯一

| 欄位 | 型別 | 說明 |
|------|------|------|
| GUID | TEXT (PK) | 彈性設定 ID |
| Dept_GUID | TEXT (FK) | 部門 |
| FlexMinutes | INTEGER | 彈性分鐘數 |
| IsDeleted | BOOLEAN | 軟刪除 |
| DeletedTime | DATETIME | 刪除時間 |
| DeletedBy | TEXT | 刪除人 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

#### RequiredConfigs（規則版本快照，不可變）
| 欄位 | 型別 | 說明 |
|------|------|------|
| GUID | TEXT (PK) | 規則版本 ID |
| Dept_GUID | TEXT (FK) | 部門 |
| Schedule_GUID | TEXT (FK) | 來源班表 |
| FlexSetting_GUID | TEXT (FK) | 來源彈性設定 |
| ActiveDay | INTEGER | 快照 |
| RequiredIn | TIME | 上班時間快照 |
| RequiredOut | TIME | 下班時間快照 |
| FlexMinutes | INTEGER | 彈性分鐘快照 |
| DayCutoff | TIME | 日切點快照 |
| EffectiveFrom | DATE | 生效日 |
| EffectiveTo | DATE | 失效日（NULL=仍有效） |
| CreateTime | DATETIME | 發佈時間 |

#### ScanEvents（原始刷卡事件）
| 欄位 | 型別 | 說明 |
|------|------|------|
| GUID | TEXT (PK) | 事件 ID |
| RFID_ID | TEXT (FK) | 員工卡 |
| Device_ID | TEXT | 讀卡器 |
| EventTime | DATETIME | 刷卡時間 |
| CreateTime | DATETIME | 寫入時間 |

#### AttendanceDaily（每日考勤結果）
| 欄位 | 型別 | 說明 |
|------|------|------|
| GUID | TEXT (PK) | 考勤結果 ID |
| RFID_ID | TEXT (FK) | 員工 |
| WorkDate | DATE | 考勤歸屬日 |
| RequiredConfigGUID | TEXT (FK) | 使用的規則版本 |
| FirstInTime | DATETIME | 第一筆刷卡 |
| LastOutTime | DATETIME | 最後一筆刷卡 |
| CheckInStatus | INTEGER | 0=NORMAL,1=FLEX,2=LATE |
| CheckOutStatus | INTEGER | 0=NORMAL,1=EARLY,2=MISSING |
| ExceptionFlags | TEXT | 例外標記 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

---

## API 設計規範

### 各資源 API 端點

#### Departments（部門）
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/departments | 取得部門列表 |
| GET | /api/departments/{guid} | 取得單一部門 |
| POST | /api/departments | 新增部門 |
| PUT | /api/departments/{guid} | 更新部門 |
| DELETE | /api/departments/{guid} | 刪除部門 |

#### Employees（員工）
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/employees | 取得員工列表 |
| GET | /api/employees/{rfid_id} | 取得單一員工 |
| PUT | /api/employees/{rfid_id} | 更新員工資料 |
| DELETE | /api/employees/{rfid_id} | 刪除員工 |

#### Schedules（班表）
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/schedules | 取得班表列表 |
| GET | /api/schedules/{guid} | 取得單一班表 |
| POST | /api/schedules | 新增班表 |
| PUT | /api/schedules/{guid} | 更新班表 |
| DELETE | /api/schedules/{guid} | 刪除班表（軟刪除） |

#### FlexSettings（彈性設定）
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/flex-settings | 取得彈性設定列表 |
| GET | /api/flex-settings/{guid} | 取得單一彈性設定 |
| POST | /api/flex-settings | 新增彈性設定 |
| PUT | /api/flex-settings/{guid} | 更新彈性設定 |
| DELETE | /api/flex-settings/{guid} | 刪除彈性設定（軟刪除） |

#### AttendanceDaily（每日考勤）
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/attendance-daily | 取得考勤記錄列表 |
| GET | /api/attendance-daily/{guid} | 取得單一考勤記錄 |
| PUT | /api/attendance-daily/{guid} | 更新考勤記錄 |
| DELETE | /api/attendance-daily/{guid} | 刪除考勤記錄 |

#### 特殊端點
| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | /api/scan | RFID 刷卡事件（核心打卡 API） |

### 路徑命名
- 使用**複數名詞**小寫 kebab-case：`/api/departments`、`/api/scan-events`
- 資源層級關係：`/api/departments/{dept_id}/employees`
- 動作端點：`POST /api/scan`（特殊操作）
- 所有端點加上 `/api` 前綴

### HTTP 狀態碼
| 狀態碼 | 用途 |
|--------|------|
| 200 OK | 成功取得/更新資源 |
| 201 Created | 成功建立資源 |
| 204 No Content | 成功刪除資源 |
| 400 Bad Request | 請求參數錯誤 |
| 401 Unauthorized | 未認證 |
| 403 Forbidden | 無權限 |
| 404 Not Found | 資源不存在 |
| 409 Conflict | 資源衝突（如重複） |
| 422 Unprocessable Entity | 驗證失敗 |
| 500 Internal Server Error | 伺服器錯誤 |

### 錯誤回應格式（FastAPI 預設）
```json
{
  "detail": "錯誤描述訊息"
}
```

驗證錯誤：
```json
{
  "detail": [
    {"loc": ["body", "field_name"], "msg": "錯誤訊息", "type": "error_type"}
  ]
}
```

### 分頁參數
```
GET /api/employees?skip=0&limit=20
```

回應 Header:
- `X-Total-Count`: 總筆數

---

## 參考文件

完整系統設計規格（中文）：`rfid_attendance_design.md`
