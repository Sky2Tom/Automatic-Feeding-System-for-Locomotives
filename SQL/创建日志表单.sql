-- 使用新创建的数据库
USE [RailwayCoalManagement];
GO
-- 1. 火车型号审计日志表
CREATE TABLE [TrainModelAuditLog] (
    [LogID] INT IDENTITY(1,1) NOT NULL,
    [TrainTypeID] VARCHAR(50) NOT NULL,
    [OperationType] VARCHAR(20) NOT NULL,
    [OperationTime] DATETIME NOT NULL DEFAULT GETDATE(),
    [Old_HoldType] VARCHAR(50) NULL,
    [New_HoldType] VARCHAR(50) NULL,
    [Old_ExLength] FLOAT NULL,
    [New_ExLength] FLOAT NULL,
    [Old_ExHeight] FLOAT NULL,
    [New_ExHeight] FLOAT NULL,
    [Old_ExWidth] FLOAT NULL,
    [New_ExWidth] FLOAT NULL,
    [Old_InLength] FLOAT NULL,
    [New_InLength] FLOAT NULL,
    [Old_InHeight] FLOAT NULL,
    [New_InHeight] FLOAT NULL,
    [Old_InWidth] FLOAT NULL,
    [New_InWidth] FLOAT NULL,
    [Old_Volume] FLOAT NULL,
    [New_Volume] FLOAT NULL,
    [Operator] VARCHAR(50) NOT NULL,
    CONSTRAINT [PK_TrainModelAuditLog] PRIMARY KEY CLUSTERED ([LogID] ASC)
);

-- 2. 系统告警表 check
CREATE TABLE [TransactionSystemAlerts] (
    [AlertID] VARCHAR(50) NOT NULL,
    [AlertType] VARCHAR(50),
    [WarehouseID] VARCHAR(50),
    [AlertTime] DATETIME,
    [Status] VARCHAR(100),
    [IsResolved] BIT DEFAULT 0,
    CONSTRAINT [PK_SystemAlerts] PRIMARY KEY CLUSTERED ([AlertID] ASC)
);

-- 3. 速度告警表
CREATE TABLE [SpeedAlerts] (
    [AlertID] VARCHAR(50) NOT NULL,
    [TrainID] VARCHAR(20) NOT NULL,
    [TrainTypeID] VARCHAR(50) NOT NULL,
    [Speed] FLOAT,
    [SpeedLimit] FLOAT,
    [AlertTime] DATETIME,
    CONSTRAINT [PK_SpeedAlerts] PRIMARY KEY CLUSTERED ([AlertID] ASC)
);