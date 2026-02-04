-- ============================================
-- RFID Attendance System - Sample Data
-- 範例資料（測試用）
-- ============================================

-- ============================================
-- 1. Departments（部門）
-- ============================================
INSERT INTO Departments (GUID, DeptCode, DeptName, CreateTime, UpdateTime)
VALUES
    ('dept-001-guid', 'IT', '資訊部', datetime('now'), datetime('now')),
    ('dept-002-guid', 'HR', '人資部', datetime('now'), datetime('now')),
    ('dept-003-guid', 'FIN', '財務部', datetime('now'), datetime('now'));

-- ============================================
-- 2. Employees（員工）
-- ============================================
INSERT INTO Employees (RFID_ID, EmpCode, Name, Dept_GUID, Active, CreateTime, UpdateTime)
VALUES
    ('RFID001', 'EMP001', '王小明', 'dept-001-guid', 1, datetime('now'), datetime('now')),
    ('RFID002', 'EMP002', '李小華', 'dept-001-guid', 1, datetime('now'), datetime('now')),
    ('RFID003', 'EMP003', '張美玲', 'dept-002-guid', 1, datetime('now'), datetime('now')),
    ('RFID004', 'EMP004', '陳大文', 'dept-003-guid', 1, datetime('now'), datetime('now')),
    ('RFID005', 'EMP005', '林志偉', 'dept-001-guid', 0, datetime('now'), datetime('now'));  -- 離職員工

-- ============================================
-- 3. Schedules（班表）
-- ============================================
-- IT 部門 - 標準班（全年適用）
INSERT INTO Schedules (
    GUID, Dept_GUID, Name, ActiveDay,
    CheckInNeedBefore, CheckNeedOutAfter, DayCutoff,
    IsDeleted, CreateTime, UpdateTime
)
VALUES
    ('schedule-001-guid', 'dept-001-guid', '標準班', 8, '09:00:00', '18:00:00', '04:00:00', 0, datetime('now'), datetime('now')),
    ('schedule-002-guid', 'dept-002-guid', '標準班', 8, '08:30:00', '17:30:00', '04:00:00', 0, datetime('now'), datetime('now')),
    ('schedule-003-guid', 'dept-003-guid', '標準班', 8, '09:00:00', '18:00:00', '04:00:00', 0, datetime('now'), datetime('now'));

-- ============================================
-- 4. FlexSettings（彈性設定）
-- ============================================
INSERT INTO FlexSettings (
    GUID, Dept_GUID, FlexMinutes,
    IsDeleted, CreateTime, UpdateTime
)
VALUES
    ('flex-001-guid', 'dept-001-guid', 30, 0, datetime('now'), datetime('now')),  -- IT: 30 分鐘彈性
    ('flex-002-guid', 'dept-002-guid', 15, 0, datetime('now'), datetime('now')),  -- HR: 15 分鐘彈性
    ('flex-003-guid', 'dept-003-guid', 0, 0, datetime('now'), datetime('now'));   -- FIN: 無彈性

-- ============================================
-- 5. RequiredConfigs（規則版本快照）
-- ============================================
INSERT INTO RequiredConfigs (
    GUID, Dept_GUID, Schedule_GUID, FlexSetting_GUID,
    ActiveDay, RequiredIn, RequiredOut, FlexMinutes, DayCutoff,
    EffectiveFrom, EffectiveTo, CreateTime
)
VALUES
    ('config-001-guid', 'dept-001-guid', 'schedule-001-guid', 'flex-001-guid', 8, '09:00:00', '18:00:00', 30, '04:00:00', '2026-01-01', NULL, datetime('now')),
    ('config-002-guid', 'dept-002-guid', 'schedule-002-guid', 'flex-002-guid', 8, '08:30:00', '17:30:00', 15, '04:00:00', '2026-01-01', NULL, datetime('now')),
    ('config-003-guid', 'dept-003-guid', 'schedule-003-guid', 'flex-003-guid', 8, '09:00:00', '18:00:00', 0, '04:00:00', '2026-01-01', NULL, datetime('now'));

-- ============================================
-- 6. ScanEvents（刷卡事件範例）
-- ============================================
INSERT INTO ScanEvents (GUID, RFID_ID, Device_ID, EventTime, CreateTime)
VALUES
    ('scan-001-guid', 'RFID001', 'DEVICE-01', '2026-02-04 08:55:00', datetime('now')),  -- 王小明上班
    ('scan-002-guid', 'RFID001', 'DEVICE-01', '2026-02-04 18:05:00', datetime('now')),  -- 王小明下班
    ('scan-003-guid', 'RFID002', 'DEVICE-01', '2026-02-04 09:15:00', datetime('now')),  -- 李小華上班（彈性時間內）
    ('scan-004-guid', 'RFID002', 'DEVICE-01', '2026-02-04 18:30:00', datetime('now'));  -- 李小華下班

-- ============================================
-- 7. AttendanceDaily（每日考勤範例）
-- ============================================
INSERT INTO AttendanceDaily (
    GUID, RFID_ID, WorkDate, RequiredConfigGUID,
    FirstInTime, LastOutTime, CheckInStatus, CheckOutStatus,
    ExceptionFlags, CreateTime, UpdateTime
)
VALUES
    ('attendance-001-guid', 'RFID001', '2026-02-04', 'config-001-guid', '2026-02-04 08:55:00', '2026-02-04 18:05:00', 0, 0, NULL, datetime('now'), datetime('now')),  -- 正常
    ('attendance-002-guid', 'RFID002', '2026-02-04', 'config-001-guid', '2026-02-04 09:15:00', '2026-02-04 18:30:00', 1, 0, NULL, datetime('now'), datetime('now'));  -- 彈性上班

-- ============================================
-- 範例資料說明
-- ============================================
-- 部門：
--   - IT（資訊部）：30 分鐘彈性，09:00-18:00
--   - HR（人資部）：15 分鐘彈性，08:30-17:30
--   - FIN（財務部）：無彈性，09:00-18:00
--
-- 員工：
--   - 王小明（RFID001）：IT 部門，在職
--   - 李小華（RFID002）：IT 部門，在職
--   - 張美玲（RFID003）：HR 部門，在職
--   - 陳大文（RFID004）：FIN 部門，在職
--   - 林志偉（RFID005）：IT 部門，離職
--
-- CheckInStatus: 0=NORMAL, 1=FLEX, 2=LATE
-- CheckOutStatus: 0=NORMAL, 1=EARLY, 2=MISSING
-- ============================================
