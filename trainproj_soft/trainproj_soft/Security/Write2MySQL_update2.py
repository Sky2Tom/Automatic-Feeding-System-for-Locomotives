
import requests
from datetime import datetime

def Write2MySQL(model, dut_number_name, dut_number_value, station, fix_id, pc_mac,
                is_pass, elapsed,
                retry_cnt, is_misdetect, defect_type_code, test_key_value,
                product_mac, product_uuid, MES_station_passing_information,
                product_type,
                test_start_time,
                Work_order_number, SN, production_processes,
                product_model, test_end_time, dut_order_code,
                product_quantity, test_item_info):

    # 数据库 API 的请求 URL
    url = "http://192.168.66.206:8000/write2mysql/"

    date_format = "%Y-%m-%d %H:%M:%S"
    datetime_object = datetime.strptime(test_start_time, date_format)
    test_time=str(datetime.date(datetime_object))


    # 请求数据
    data = {
    "ProductTesting": {
        "model": "Testing Model",
        "dut_number_name": "DUT",
        "dut_number_value": "DUT Number Value",
        "station": "Station",
        "fix_id": "Fix ID",
        "pc_mac": "PC MAC",
        "is_pass": "True",
        "elapsed": 10,
        "retry_cnt": 3,
        "is_misdetect": "False",
        "defect_type_code": "Defect Type Code",
        "test_key_value": "Test Key Value",
        "product_mac": "Product MAC",
        "product_uuid": "Product UUID",
        "mes_station_passing_information": "MES Station Passing Information",
        "product_type": "Product Type",
        "test_start_time": "2010-01-02 12:00:00",
        "work_order_number": "Work Order Number",
        "sn": "SN",
        "production_processes": "Production Processes",
        "product_model": "Product Model",
        "test_end_time": "2010-01-02 12:00:00",
        "dut_order_code": "DUT Order Code81",
    },
    "TestItem": [],
    "StatisticalReport": {
        "work_order_number2": "DUT Order Code81",  # 和和ProductTesting中的dut_order_code一样
        "product_model": "Product Model",  # 产品型号和ProductTesting中的product_model一样
        "product_quantity": 100,
        "test_time": "2010-01-02",  # 和ProductTesting中的test_end_time的年月日一样
        "actual_quantity": 0,  # 这三个数值都为0
        "success": 0,
        "failed": 0,
    },
}


    data["ProductTesting"]["model"] = model
    data["ProductTesting"]["dut_number_name"] = dut_number_name
    data["ProductTesting"]["dut_number_value"] = dut_number_value
    data["ProductTesting"]["station"] = station
    data["ProductTesting"]["fix_id"] = fix_id
    data["ProductTesting"]["pc_mac"] = pc_mac
    data["ProductTesting"]["is_pass"] = is_pass
    data["ProductTesting"]["elapsed"] = elapsed
    data["ProductTesting"]["retry_cnt"] = retry_cnt
    data["ProductTesting"]["is_misdetect"] = is_misdetect
    data["ProductTesting"]["defect_type_code"] = defect_type_code
    data["ProductTesting"]["test_key_value"] = test_key_value
    data["ProductTesting"]["product_mac"] = product_mac
    data["ProductTesting"]["product_uuid"] = product_uuid
    data["ProductTesting"]["mes_station_passing_information"] = MES_station_passing_information
    data["ProductTesting"]["product_type"] = product_type
    data["ProductTesting"]["test_start_time"] = test_start_time
    data["ProductTesting"]["work_order_number"] = Work_order_number
    data["ProductTesting"]["sn"] = SN
    data["ProductTesting"]["production_processes"] = production_processes
    data["ProductTesting"]["product_model"] = product_model
    data["ProductTesting"]["test_end_time"] = test_end_time
    data["ProductTesting"]["dut_order_code"] = dut_order_code

    data["StatisticalReport"]["work_order_number2"] = dut_order_code
    data["StatisticalReport"]["product_model"] = product_model
    data["StatisticalReport"]["product_quantity"] = product_quantity
    data["StatisticalReport"]["test_time"] = test_time

    for info in test_item_info:
        data["TestItem"].append({
            "name": info[0],
            "value": info[1],
            "elapsed_item": info[2],
            "result_item": info[3],
        })

    # print(type(data))
    # print(data)

    # 发送 POST 请求
    try:
        response = requests.post(url, json=data)

        if response.status_code == 201 or 500:
            print("成功创建资源")
        else:
            print("请求失败")
        print(response.status_code)  # 打印状态码
    except requests.exceptions.RequestException as e:
        print("请求异常：", e)