-- 使用数据库
USE [RailwayCoalManagement];
GO

-- 1. 火车型号修改审计触发器 (check)
CREATE TRIGGER tr_TrainModel_AuditUpdate
ON [Train Model Table]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO TrainModelAuditLog (
        TrainTypeID, OperationType, OperationTime, 
        Old_HoldType, New_HoldType,
        Old_ExLength, New_ExLength,
		Old_ExHeight, New_ExHeight,
		Old_ExWidth, New_ExWidth,
		Old_InLength, New_InLength,
		Old_InHeight, New_InHeight,
		Old_InWidth, New_InWidth,
        Old_Volume, New_Volume,
        Operator
    )
    SELECT 
        i.TrainTypeID, 'UPDATE', GETDATE(),
        d.HoldType, i.HoldType,
        d.ExLength, i.ExLength,
		d.ExHeight, i.ExHeight,
		d.ExWidth, i.ExWidth,
        d.InLength, i.InLength,
		d.InHeight, i.InHeight,
		d.InWidth, i.InWidth,
        d.Volume, i.Volume,
        SYSTEM_USER
    FROM inserted i
    JOIN deleted d ON i.TrainTypeID = d.TrainTypeID;
END;
GO

-- 2. 火车型号删除限制触发器(check)
-- 业务逻辑：如果该火车型号正在加料，则无法在数据库中删除这种型号的列车
CREATE TRIGGER tr_TrainModel_PreventDeleteIfInUse
ON [Train Model Table]
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (
        SELECT 1 FROM deleted d
        JOIN [Train Arrival Table] t ON d.TrainTypeID = t.TrainTypeID
    )
    BEGIN
        RAISERROR('Cannot delete train model that is currently in use by active trains.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;
    
    DELETE FROM [Train Model Table]
    WHERE TrainTypeID IN (SELECT TrainTypeID FROM deleted);
END;
GO


-- 3. 牵引系统状态异常触发器（check）
-- Transaction Status 正常为1，异常为0
CREATE TRIGGER tr_TransactionStatus_Alert
ON [Transaction Status Table]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (
        SELECT 1 FROM inserted 
        WHERE [Transaction Status] <> 1
    )
    BEGIN
        INSERT INTO TransactionSystemAlerts (AlertType, WarehouseID, AlertTime, Status)
        SELECT '牵引系统异常', WarehouseID, GETDATE(), [Transaction Status]
        FROM inserted
        WHERE [Transaction Status] <> 1;

    END;
END;
GO

-- 5. 超速检测与告警触发器（check）
CREATE TRIGGER tr_TrainSpeed_OverspeedCheck
ON [Train Speed Table]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @SpeedThreshold FLOAT = 60.0; -- 设定固定速度阈值为60 km/h
    
    -- 更新超速标志
    UPDATE ts
    SET ts.Overspeed = CASE WHEN i.Speed > @SpeedThreshold THEN 'Y' ELSE 'N' END
    FROM [Train Speed Table] ts
    JOIN inserted i ON ts.ID = i.ID;
    
    -- 记录超速告警
    INSERT INTO SpeedAlerts (TrainID, TrainTypeID, Speed, SpeedLimit, AlertTime)
    SELECT 
        i.TrainID, 
        i.TrainTypeID, 
        i.Speed, 
        @SpeedThreshold, -- 使用固定阈值作为速度限制
        GETDATE()
    FROM inserted i
    WHERE i.Speed > @SpeedThreshold;
END;
GO

-- 6. 车厢入库触发器 - 检查是否已有相同车号的入库记录（check）
-- 确保车厢有入库就一定会有出库，否则会有告警提醒
CREATE TRIGGER tr_Inventory_CheckDuplicate
ON [Inventory Table]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- 检查是否有重复入库的车厢
    IF EXISTS (
        SELECT 1 FROM inserted i
        JOIN [Inventory Table] it ON i.TrainID = it.TrainID
        WHERE it.InTime < i.InTime AND it.TrainID = i.TrainID
        AND NOT EXISTS (
            SELECT 1 FROM [Delivery Table] d 
            WHERE d.TrainID = it.TrainID AND d.OutTime > it.InTime
        )
    )
    BEGIN
        RAISERROR('该车厢已有入库记录但未出库，不能重复入库', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;
END;
GO
