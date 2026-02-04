-- ============================================
-- RFID Attendance System - Database Schema
-- SQLite Version
-- ============================================

-- 啟用外鍵約束
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. Departments（部門）
-- ============================================
CREATE TABLE IF NOT EXISTS Departments (
    GUID TEXT PRIMARY KEY,
    DeptCode TEXT NOT NULL UNIQUE,
    DeptName TEXT NOT NULL,
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IX_Departments_DeptCode ON Departments(DeptCode);

-- ============================================
-- 2. Employees（員工）
-- ============================================
CREATE TABLE IF NOT EXISTS Employees (
    RFID_ID TEXT PRIMARY KEY,
    EmpCode TEXT NOT NULL UNIQUE,
    Name TEXT NOT NULL,
    Dept_GUID TEXT NOT NULL,
    Active INTEGER NOT NULL DEFAULT 1,
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_Employees_Dept_GUID FOREIGN KEY (Dept_GUID)
        REFERENCES Departments(GUID) ON DELETE RESTRICT
);

CREATE INDEX IX_Employees_Dept_GUID ON Employees(Dept_GUID);
CREATE INDEX IX_Employees_EmpCode ON Employees(EmpCode);
CREATE INDEX IX_Employees_Active ON Employees(Active);

-- ============================================
-- 3. Schedules（部門班表，軟刪除）
-- 唯一約束：(Dept_GUID, ActiveDay) 在 IsDeleted = 0 下唯一
-- ============================================
CREATE TABLE IF NOT EXISTS Schedules (
    GUID TEXT PRIMARY KEY,
    Dept_GUID TEXT NOT NULL,
    Name TEXT NOT NULL,
    ActiveDay INTEGER NOT NULL CHECK (ActiveDay >= 1 AND ActiveDay <= 8),
    CheckInNeedBefore TIME NOT NULL,
    CheckNeedOutAfter TIME NOT NULL,
    DayCutoff TIME NOT NULL DEFAULT '04:00:00',
    IsDeleted INTEGER NOT NULL DEFAULT 0,
    DeletedTime DATETIME,
    DeletedBy TEXT,
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_Schedules_Dept_GUID FOREIGN KEY (Dept_GUID)
        REFERENCES Departments(GUID) ON DELETE RESTRICT
);

CREATE INDEX IX_Schedules_Dept_GUID ON Schedules(Dept_GUID);
CREATE INDEX IX_Schedules_ActiveDay ON Schedules(ActiveDay);
CREATE INDEX IX_Schedules_IsDeleted ON Schedules(IsDeleted);

-- 唯一約束：每個部門每個 ActiveDay 只能有一個有效班表
CREATE UNIQUE INDEX UQ_Schedules_Dept_ActiveDay
    ON Schedules(Dept_GUID, ActiveDay)
    WHERE IsDeleted = 0;

-- ============================================
-- 4. FlexSettings（彈性設定，軟刪除）
-- 唯一約束：Dept_GUID 在 IsDeleted = 0 下唯一
-- ============================================
CREATE TABLE IF NOT EXISTS FlexSettings (
    GUID TEXT PRIMARY KEY,
    Dept_GUID TEXT NOT NULL,
    FlexMinutes INTEGER NOT NULL DEFAULT 0,
    IsDeleted INTEGER NOT NULL DEFAULT 0,
    DeletedTime DATETIME,
    DeletedBy TEXT,
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_FlexSettings_Dept_GUID FOREIGN KEY (Dept_GUID)
        REFERENCES Departments(GUID) ON DELETE RESTRICT
);

CREATE INDEX IX_FlexSettings_Dept_GUID ON FlexSettings(Dept_GUID);
CREATE INDEX IX_FlexSettings_IsDeleted ON FlexSettings(IsDeleted);

-- 唯一約束：每個部門只能有一個有效彈性設定
CREATE UNIQUE INDEX UQ_FlexSettings_Dept
    ON FlexSettings(Dept_GUID)
    WHERE IsDeleted = 0;

-- ============================================
-- 5. RequiredConfigs（規則版本快照，不可變）
-- ============================================
CREATE TABLE IF NOT EXISTS RequiredConfigs (
    GUID TEXT PRIMARY KEY,
    Dept_GUID TEXT NOT NULL,
    Schedule_GUID TEXT,
    FlexSetting_GUID TEXT,
    ActiveDay INTEGER NOT NULL CHECK (ActiveDay >= 1 AND ActiveDay <= 8),
    RequiredIn TIME NOT NULL,
    RequiredOut TIME NOT NULL,
    FlexMinutes INTEGER NOT NULL DEFAULT 0,
    DayCutoff TIME NOT NULL DEFAULT '04:00:00',
    EffectiveFrom DATE NOT NULL,
    EffectiveTo DATE,
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_RequiredConfigs_Dept_GUID FOREIGN KEY (Dept_GUID)
        REFERENCES Departments(GUID) ON DELETE RESTRICT,
    CONSTRAINT FK_RequiredConfigs_Schedule_GUID FOREIGN KEY (Schedule_GUID)
        REFERENCES Schedules(GUID) ON DELETE RESTRICT,
    CONSTRAINT FK_RequiredConfigs_FlexSetting_GUID FOREIGN KEY (FlexSetting_GUID)
        REFERENCES FlexSettings(GUID) ON DELETE RESTRICT
);

CREATE INDEX IX_RequiredConfigs_Dept_GUID ON RequiredConfigs(Dept_GUID);
CREATE INDEX IX_RequiredConfigs_EffectiveFrom ON RequiredConfigs(EffectiveFrom);
CREATE INDEX IX_RequiredConfigs_EffectiveTo ON RequiredConfigs(EffectiveTo);
CREATE INDEX IX_RequiredConfigs_ActiveDay ON RequiredConfigs(ActiveDay);

-- ============================================
-- 6. ScanEvents（原始刷卡事件）
-- ============================================
CREATE TABLE IF NOT EXISTS ScanEvents (
    GUID TEXT PRIMARY KEY,
    RFID_ID TEXT NOT NULL,
    Device_ID TEXT,
    EventTime DATETIME NOT NULL,
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_ScanEvents_RFID_ID FOREIGN KEY (RFID_ID)
        REFERENCES Employees(RFID_ID) ON DELETE RESTRICT
);

CREATE INDEX IX_ScanEvents_RFID_ID ON ScanEvents(RFID_ID);
CREATE INDEX IX_ScanEvents_EventTime ON ScanEvents(EventTime);
CREATE INDEX IX_ScanEvents_Device_ID ON ScanEvents(Device_ID);

-- ============================================
-- 7. AttendanceDaily（每日考勤結果）
-- ============================================
CREATE TABLE IF NOT EXISTS AttendanceDaily (
    GUID TEXT PRIMARY KEY,
    RFID_ID TEXT NOT NULL,
    WorkDate DATE NOT NULL,
    RequiredConfigGUID TEXT,
    FirstInTime DATETIME,
    LastOutTime DATETIME,
    CheckInStatus INTEGER DEFAULT NULL,
    CheckOutStatus INTEGER DEFAULT NULL,
    ExceptionFlags TEXT,
    CreateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_AttendanceDaily_RFID_ID FOREIGN KEY (RFID_ID)
        REFERENCES Employees(RFID_ID) ON DELETE RESTRICT,
    CONSTRAINT FK_AttendanceDaily_RequiredConfigGUID FOREIGN KEY (RequiredConfigGUID)
        REFERENCES RequiredConfigs(GUID) ON DELETE RESTRICT
);

-- 唯一約束：每位員工每個工作日只能有一筆記錄
CREATE UNIQUE INDEX UQ_AttendanceDaily_RFID_WorkDate
    ON AttendanceDaily(RFID_ID, WorkDate);

CREATE INDEX IX_AttendanceDaily_RFID_ID ON AttendanceDaily(RFID_ID);
CREATE INDEX IX_AttendanceDaily_WorkDate ON AttendanceDaily(WorkDate);
CREATE INDEX IX_AttendanceDaily_CheckInStatus ON AttendanceDaily(CheckInStatus);
CREATE INDEX IX_AttendanceDaily_CheckOutStatus ON AttendanceDaily(CheckOutStatus);

-- ============================================
-- 狀態列舉說明（參考用）
-- ============================================
-- CheckInStatus:
--   0 = NORMAL（正常）
--   1 = FLEX（在彈性時間內）
--   2 = LATE（遲到）
--
-- CheckOutStatus:
--   0 = NORMAL（正常）
--   1 = EARLY（早退）
--   2 = MISSING（缺卡）
--
-- ActiveDay:
--   1-7 = 週一至週日
--   8 = 全年適用
-- ============================================
