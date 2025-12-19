-- 使用新创建的数据库
USE [RailwayCoalManagement];
GO

-- 创建火车型号表
CREATE TABLE [Train Model Table] (
    [TrainTypeID] VARCHAR(50) NOT NULL,
    [HoldType] VARCHAR(50),
    [ExLength] FLOAT,
    [ExWidth] FLOAT,
    [ExHeight] FLOAT,
    [InLength] FLOAT,
    [InWidth] FLOAT,
    [InHeight] FLOAT,
    [Volume] FLOAT,
    [Density] FLOAT ,
    [LoadWeight] FLOAT,
    [FullLength] FLOAT,
    [BottomHeight] FLOAT,
    [HookType] VARCHAR(50),
    CONSTRAINT [PK_TrainModel] PRIMARY KEY CLUSTERED ([TrainTypeID] ASC)
);

-- 创建火车到位表
CREATE TABLE [Train Arrival Table] (
    [TrainID] VARCHAR(50) NOT NULL,
    [TrainTypeID] VARCHAR(50) NOT NULL,
    [WarehouseID] VARCHAR(50) NOT NULL,
    [WarehouseName] VARCHAR(50) ,
    [OnPosition] VARCHAR(20),
    [Time] DATETIME,
    CONSTRAINT [PK_TrainArrival] PRIMARY KEY CLUSTERED ([TrainID] ASC),
    CONSTRAINT [FK_TrainArrival_TrainModel] FOREIGN KEY ([TrainTypeID]) 
        REFERENCES [Train Model Table] ([TrainTypeID])
);

-- 创建牵引系统状态表
CREATE TABLE [Transaction Status Table] (
    [ID] VARCHAR(50) NOT NULL,
    [WarehouseID] VARCHAR(50) NOT NULL,
    [WarehouseName] VARCHAR(50),
    [Transaction Status] INT,
    [Time] DATETIME,
    CONSTRAINT [PK_TransactionStatus] PRIMARY KEY CLUSTERED ([ID] ASC)
);

-- 创建火车速度表
CREATE TABLE [Train Speed Table] (
    [ID] VARCHAR(50) NOT NULL,
    [TrainID] VARCHAR(20) NOT NULL,
    [TrainTypeID] VARCHAR(50) NOT NULL, 
    [WarehouseID] VARCHAR(20) NOT NULL,
    [Speed] FLOAT,
    [Overspeed] INT,
    [Time] DATETIME,
    CONSTRAINT [PK_TrainSpeed] PRIMARY KEY CLUSTERED ([ID] ASC)
);

-- 创建防撞告警表
CREATE TABLE [Warning Table] (
    [ID] VARCHAR(50)  NOT NULL,
    [TrainID] VARCHAR(20) NOT NULL,
    [TrainTypeID] VARCHAR(50) NOT NULL, 
    [WarehouseID] VARCHAR(20) NOT NULL,
    [Warning] VARCHAR(20), 
    [Overspeed] VARCHAR(20),
    [Time] DATETIME,
    CONSTRAINT [PK_Warning] PRIMARY KEY CLUSTERED ([ID] ASC)
);

-- 创建车厢入库表
CREATE TABLE [Inventory Table] (
    [ID] VARCHAR(50) NOT NULL,
    [TrainID] VARCHAR(20) NOT NULL,
    [TrainTypeID] VARCHAR(50) NOT NULL, 
    [WarehouseID] VARCHAR(20) NOT NULL,
    [Reporter] VARCHAR(50), 
    [InTime] DATETIME,
    CONSTRAINT [PK_Inventory] PRIMARY KEY CLUSTERED ([ID] ASC)
);

-- 创建车厢出库表
CREATE TABLE [Delivery Table] (
    [ID] VARCHAR(50) NOT NULL,
    [TrainID] VARCHAR(20) NOT NULL,
    [TrainTypeID] VARCHAR(50) NOT NULL,
    [WarehouseID] VARCHAR(20) NOT NULL,
    [Reporter] VARCHAR(50) NOT NULL,
    [OutTime] DATETIME NOT NULL,
    CONSTRAINT [PK_Delivery] PRIMARY KEY CLUSTERED ([ID] ASC)
);

-- 创建下料记录表（修正时间字段为DATETIME）
CREATE TABLE [Layoff History Table] (
    [ContractID] VARCHAR(50)  NOT NULL,
    [WarehouseID] VARCHAR(20) NOT NULL,
    [MachineID] VARCHAR(80) NOT NULL,
	[Layoff_Volume]DECIMAL(18,2) NOT NULL,
    [Time] DATETIME,
    CONSTRAINT [PK_LayoffHistory] PRIMARY KEY CLUSTERED ([ContractID] ASC)
);

-- 创建下料中断表
CREATE TABLE [Layoff Break Table] (
    [AccountID] VARCHAR(50) NOT NULL,
    [WarehouseID] VARCHAR(20) NOT NULL,
    [MachineID] VARCHAR(20) NOT NULL,
    [Reason] VARCHAR(50),
    [Time] DATETIME,  -- 从CHAR(20)改为DATETIME
    CONSTRAINT [PK_LayoffBreak] PRIMARY KEY CLUSTERED ([AccountID] ASC)
);

-- 创建下煤机表（修正数值字段为适当类型）
CREATE TABLE [Machine Table] (
    [MaterialID] VARCHAR(20) NOT NULL,
    [WarehouseID] VARCHAR(50) NOT NULL,
    [Volume] DECIMAL(18,2), 
    [Reporter] VARCHAR(20),
    [OpenStatus] VARCHAR(20),
    [RunStatus] VARCHAR(20),
    CONSTRAINT [PK_Machine] PRIMARY KEY CLUSTERED ([MaterialID] ASC)
);

-- 现在可以成功添加外键约束
ALTER TABLE [Train Speed Table] 
ADD CONSTRAINT [FK_TrainSpeed_TrainModel] 
FOREIGN KEY ([TrainTypeID]) REFERENCES [Train Model Table] ([TrainTypeID]);

ALTER TABLE [Warning Table] 
ADD CONSTRAINT [FK_Warning_TrainModel] 
FOREIGN KEY ([TrainTypeID]) REFERENCES [Train Model Table] ([TrainTypeID]);

ALTER TABLE [Inventory Table] 
ADD CONSTRAINT [FK_Inventory_TrainModel] 
FOREIGN KEY ([TrainTypeID]) REFERENCES [Train Model Table] ([TrainTypeID]);

ALTER TABLE [Delivery Table] 
ADD CONSTRAINT [FK_Delivery_TrainModel] 
FOREIGN KEY ([TrainTypeID]) REFERENCES [Train Model Table] ([TrainTypeID]);