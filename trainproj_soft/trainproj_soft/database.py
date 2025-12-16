def select_request():
    print("*"*13+"欢迎使用设备管理系统"+"*"*13)
    resource_show()

def resource_show():
    cur.execute("SELECT * FROM Train")
    row = cur.fetchone()
    while row:
        print(row)
        row = cur.fetchone()
    cur.close()
    cnxn.close()


import pyodbc
import pandas as pd
cnxn=pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-OKUMI3CM;DATABASE=train_data_managementSystem;UID=sa;PWD=220242236')
cur = cnxn.cursor()

select_request()




