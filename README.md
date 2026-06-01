# 企業 RFID 考勤系統設計文件（最終確認版）

> 本文件彙整目前已確認之 **資料庫設計（DB Schema）** 與 **完整打卡流程（Flow / DB Logic）**，
> 作為 RD、SA、HR 與未來稽核/維運的共同依據。

---

## 一、核心設計原則

1. **RFID 為唯一打卡來源**
2. **部門級規則**
   - 班表（Schedules）
   - 彈性設定（FlexSettings）
3. **規則版本化**
   - Schedules / FlexSettings 可更新
   - RequiredConfigs 為「已發佈、不可變快照」
4. **規則固定時機**
   - 當日第一筆「上班打卡」時固定 RequiredConfig
   - HR 之後的更新只影響「尚未打上班卡的人」
5. **不存可推導中間值**
   - 不存 CalcOutTime
   - 僅存結果狀態（enum）

---

## 二、資料庫結構總覽（ER Logical View）

```
Departments
 ├─ Employees
 │   ├─ ScanEvents
 │   └─ AttendanceDaily ── RequiredConfigs ── Schedules
 │                                      └─ FlexSettings
```

---

## 三、資料表設計（Final Schema）

### 3.1 Departments

| 欄位 | 型別 | 說明 |
|---|---|---|
| GUID | TEXT (PK) | 部門唯一識別 |
| DeptCode | TEXT | 部門代碼 |
| DeptName | TEXT | 部門名稱 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

---

### 3.2 Employees

| 欄位 | 型別 | 說明 |
|---|---|---|
| RFID_ID | TEXT (PK) | RFID 卡 GUID |
| EmpCode | TEXT | 員工編號 |
| Name | TEXT | 員工姓名 |
| Dept_GUID | TEXT (FK) | 所屬部門 |
| Active | BOOLEAN | 是否在職 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

---

### 3.3 Schedules（部門班表，軟刪除）

> **唯一性約束**：  
> `(Dept_GUID, ActiveDay)` 在 `IsDeleted = 0` 下唯一

| 欄位 | 型別 | 說明 |
|---|---|---|
| GUID | TEXT (PK) | 班表 ID |
| Dept_GUID | TEXT (FK) | 部門 |
| Name | TEXT | 班表名稱 |
| ActiveDay | INTEGER | 1–7（週一至週日），8=全年無休 |
| CheckInNeedBefore | TIME | 規定上班時間 (A) |
| CheckNeedOutAfter | TIME | 規定下班時間 |
| DayCutoff | TIME | 日切點（如 04:00） |
| IsDeleted | BOOLEAN | 軟刪除 |
| DeletedTime | DATETIME | 刪除時間 |
| DeletedBy | TEXT | 刪除人 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

---

### 3.4 FlexSettings（彈性設定，部門唯一，軟刪除）

> **唯一性約束**：  
> `Dept_GUID` 在 `IsDeleted = 0` 下唯一

| 欄位 | 型別 | 說明 |
|---|---|---|
| GUID | TEXT (PK) | 彈性設定 ID |
| Dept_GUID | TEXT (FK) | 部門 |
| FlexMinutes | INTEGER | 彈性分鐘數 |
| IsDeleted | BOOLEAN | 軟刪除 |
| DeletedTime | DATETIME | 刪除時間 |
| DeletedBy | TEXT | 刪除人 |
| CreateTime | DATETIME | 建立時間 |
| UpdateTime | DATETIME | 更新時間 |

---

### 3.5 RequiredConfigs（規則版本快照）

> **不可變（Immutable）**  
> 由 HR 在建立/更新 Schedules 或 FlexSettings 時發佈

| 欄位 | 型別 | 說明 |
|---|---|---|
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

---

### 3.6 ScanEvents（原始刷卡事件）

| 欄位 | 型別 | 說明 |
|---|---|---|
| GUID | TEXT (PK) | 事件 ID |
| RFID_ID | TEXT (FK) | 員工卡 |
| Device_ID | TEXT | 讀卡器 |
| EventTime | DATETIME | 刷卡時間 |
| CreateTime | DATETIME | 寫入時間 |

---

### 3.7 AttendanceDaily（每日考勤結果）

| 欄位 | 型別 | 說明 |
|---|---|---|
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

## 四、完整打卡流程（Flow / DB Logic）

### 4.1 打卡事件進入（POST /api/scan）

1. 讀取 `rfid_id`
2. 查詢 `Employees` → 驗證員工與部門
3. 依 `Dept_GUID` 查詢：
   - Schedules（ActiveDay + IsDeleted=0）
   - FlexSettings（IsDeleted=0，部門唯一）
4. 使用 `Schedule.DayCutoff` 決定 `WorkDate`
5. 寫入 `ScanEvents`
6. Upsert `AttendanceDaily (RFID_ID, WorkDate)`
   - 若不存在 → 第一筆上班卡
     - 固定 RequiredConfigGUID（選當下生效版本）
   - 若已存在 → 更新 FirstIn / LastOut（不改規則）
7. 使用 RequiredConfig 計算狀態
8. 更新 `CheckInStatus / CheckOutStatus`

---

## 五、規則固定鐵律

> **RequiredConfig 僅在「當日第一筆上班打卡」時決定一次。**  
> HR 之後更新設定，只影響尚未打上班卡的員工。

---

## 六、狀態 Enum 定義

### CheckInStatus
- 0 = NORMAL
- 1 = FLEX
- 2 = LATE

### CheckOutStatus
- 0 = NORMAL
- 1 = EARLY
- 2 = MISSING

---

## 七、設計總結

- 規則可追溯、不可被歷史污染
- DB 無冗餘中間欄位
- 班表 / 彈性設定不衝突
- 打卡路徑穩定、可擴充

> **本設計已達企業級考勤系統標準，可直接進入實作階段。**
