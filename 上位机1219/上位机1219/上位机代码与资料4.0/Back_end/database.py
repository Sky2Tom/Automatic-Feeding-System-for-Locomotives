import pyodbc
# import pandas as pd

class TrainDatabaseManager:
    def __init__(self, server, database, username, password):
        """初始化数据库连接"""
        self.connection_string = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            print("数据库连接成功!")
        except pyodbc.Error as e:
            print(f"数据库连接失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("数据库连接已关闭")
    
    def execute_query(self, query, params=None, fetch_all=True):
        """执行查询并返回结果"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if fetch_all:
                return self.cursor.fetchall()
            else:
                return self.cursor.fetchone()
        except pyodbc.Error as e:
            print(f"查询执行失败: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """执行更新操作(增删改)"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except pyodbc.Error as e:
            self.conn.rollback()
            print(f"操作执行失败: {e}")
            return False
    
    # 以下是针对各表单的专门方法
    
    # 1. 火车型号表操作
    def get_all_train_models(self):
        """获取所有火车型号"""
        return self.execute_query("SELECT * FROM [Train Model Table]")
    
    def add_train_model(self, model_data):
        """添加火车型号"""
        query = """
        INSERT INTO [Train Model Table] (
            TrainTypeID, HoldType, ExLength, ExWidth, ExHeight,
            InLength, InWidth, InHeight, Volume, Density,
            LoadWeight, FullLength, BottomHeight, HookType
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, model_data)
    
    # 2. 火车到位表操作
    def get_train_arrivals(self):
        """获取所有火车到位记录"""
        return self.execute_query("SELECT * FROM [Train Arrival Table]")
    
    def update_train_arrival_status(self, train_id, status):
        """更新火车到位状态"""
        query = """
        UPDATE [Train Arrival Table] 
        SET OnPosition = ?, Time = GETDATE()
        WHERE TrainID = ?
        """
        return self.execute_update(query, (status, train_id))
    
    # 3. 火车速度表操作
    def get_train_speeds(self):
        """获取所有火车速度记录"""
        return self.execute_query("SELECT * FROM [Train Speed Table]")
    
    def add_speed_record(self, speed_data):
        """添加速度记录"""
        query = """
        INSERT INTO [Train Speed Table] (
            TrainID, TrainTypeID, WarehouseID, Speed, Overspeed, Time
        ) VALUES (?, ?, ?, ?, ?, GETDATE())
        """
        return self.execute_update(query, speed_data)
    
    # 4. 车厢出入库操作
    def get_inventory_records(self):
        """获取所有入库记录"""
        return self.execute_query("SELECT * FROM [Inventory Table]")
    
    def add_inventory_record(self, inventory_data):
        """添加入库记录"""
        query = """
        INSERT INTO [Inventory Table] (
            TrainID, TrainTypeID, WarehouseID, Reporter, InTime
        ) VALUES (?, ?, ?, ?, GETDATE())
        """
        return self.execute_update(query, inventory_data)
    
    # 5. 下料记录操作
    def get_layoff_history(self):
        """获取所有下料记录"""
        return self.execute_query("SELECT * FROM [Layoff History Table]")
    
    def add_layoff_record(self, layoff_data):
        """添加下料记录"""
        query = """
        INSERT INTO [Layoff History Table] (
            WarehouseID, MachineID, Time
        ) VALUES (?, ?, GETDATE())
        """
        return self.execute_update(query, layoff_data)
    
    # 其他实用方法
    def show_table_data(self, table_name):
        """显示指定表的所有数据"""
        print(f"\n{'*'*20} {table_name} 数据 {'*'*20}")
        data = self.execute_query(f"SELECT * FROM [{table_name}]")
        if data:
            df = pd.DataFrame.from_records(data, columns=[column[0] for column in self.cursor.description])
            print(df.to_string(index=False))
        else:
            print("没有找到数据")
        print("*" * (40 + len(table_name)))

    def query_all(self, table: str):
        """
        查询整张表
        返回: (columns: List[str], rows: List[Tuple])
        """
        sql = f"SELECT * FROM {table}"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        return columns, rows

    def query_by_train_type_id(self, table: str, train_type_id: str):
        """
        按 TrainTypeID 精确查询
        返回: (columns: List[str], rows: List[Tuple])
        """
        sql = f"SELECT * FROM {table} WHERE TrainTypeID = ?"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, (train_type_id,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        return columns, rows


# 使用示例
if __name__ == "__main__":
    # 初始化数据库管理器
    db_manager = TrainDatabaseManager(
        server="WIN-DNI5FVM376E",
        database="RailwayCoalManagement",
        username="sa",
        password="220242236"
    )
    
    try:
        # 示例1: 显示所有火车型号
        # db_manager.show_table_data("Train Model Table")
        a=1
        
        
    finally:
        # 关闭连接
        db_manager.close()