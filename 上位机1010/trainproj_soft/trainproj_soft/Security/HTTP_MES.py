import requests, datetime, uuid, json,re

# 获取时间戳
def getTime():
    # 获取当前时间
    current_time = datetime.datetime.now()
    # 将当前时间转化为时间戳（秒级）
    timestamp = int(current_time.timestamp())
    return str(timestamp)

# SN检查接口
# {"INTERFACENO":"007", "INTERFACEDATA":"X12401MFGO0948,SN,2024011A00007,TEST001"}
def Check_SN_fun(data):
    url = "http://192.168.66.200:8015/mc/http/interface.ms?model=getData&method=exeFunc"
    keys_to_check = ['INTERFACENO','INTERFACEDATA']
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                # 请求失败
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')

# N2产测返回接口
# {"res":"OK","dateflag":"1682313357","id":"e06454250d0242898eb0155aa63c35e7","itemsn":"SN009"}
def n2TestResult(data):
    url = "http://192.168.66.201:9015/mc/http/interface.ms?model=ResultData&method=exeFunc"
    keys_to_check = ['res','dateflag','id','itemsn']
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                # 请求失败
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')




# N2产测请求接口
# {"projectid": "X12304MFG002150","itemcode": "9060010065","prodection": "ZZ","paramtype": "MAC", "dateflag": "1682150208" }
def n2TestRequest(data):
    url = "http://192.168.66.201:9015/mc/http/interface.ms?model=GetParamData&method=exeFunc"
    keys_to_check = ['projectid','itemcode','prodection','paramtype','dateflag']
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                # 请求失败
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')


# N2生产流程校验接口(**换成新的接口：流程校验SN)
# {"EMP_NO":"ch","WORK_STATION":"SMT5-1-A","M_SN":"2wzqwzq00003"}
# def n2ProductionValidation(data):
#     url = "http://192.168.66.201:9015/mc/http/interface.ms?model=BurnFlowVerify&method=exeFunc"
#     keys_to_check = ['EMP_NO','WORK_STATION','M_SN']
#     if all(key in data for key in keys_to_check):
#         response = requests.post(url, json=data)
#         if response.status_code == 200:
#             json_data = response.json()
#             return json_data
#         else:
#             print("请求失败，状态码：", response.status_code)
#             return None
#     else:
#         print('参数有误！')


# 流程校验SN
# {"M_EMP_NO":"MES","M_GROUP_NAME":"工模测试","M_SN":"GTEEJ23KD00DCE","M_MO_NUMBER":"X12310MFG000383-04"}
def ProductCheck(data):
    url = "http://192.168.66.201:9015/mc/http/interface.ms?model=ProductCheckMo&method=exeFunc"
    keys_to_check = ["M_EMP_NO","M_GROUP_NAME","M_SN","M_MO_NUMBER"]
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')

# 过站数据保存
# {"M_EMP_NO":"MES","M_GROUP_NAME":"工模测试","M_SN":"GTEEJ23KD00DCE","M_MO_NUMBER":"X12310MFG000383-04"}
def ProductStation(data):
    url = "http://192.168.66.201:9015/mc/http/interface.ms?model=ProductStationMo&method=exeFunc"
    keys_to_check = ["M_EMP_NO","M_GROUP_NAME","M_SN","M_MO_NUMBER"]
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')

# N2生产过站接口(** 换成新的过站数据保存接口)
# {"EMP_NO":"ch","WORK_STATION":"SMT5-1-A","M_SN":"2wzqwzq00004","M_RES":"FAIL","M_EC_STR":""}
# def n2ProductionPass(data):
#     # 定义URL和请求参数
#     url = "http://192.168.66.201:9015/mc/http/interface.ms?model=ProductPassStation&method=exeFunc"
#     keys_to_check = ['EMP_NO','WORK_STATION','M_SN','M_RES','M_EC_STR']
#     if all(key in data for key in keys_to_check):
#         response = requests.post(url, json=data)
#         if response.status_code == 200:
#             json_data = response.json()
#             return json_data
#         else:
#             print("请求失败，状态码：", response.status_code)
#             return None
#     else:
#         print('参数有误！')


# 获取固件URL
# {"PROJECT_ID":"X12307MFG000575","GROUP_CODE":"DIP2","ITEM_CODE":"9010010174"}
def n2GetBurnUrl(data):
    url = "http://192.168.66.200:8015/mc/http/interface.ms?model=GetBurnUrl&method=exeFunc"
    keys_to_check = ['PROJECT_ID','GROUP_CODE','ITEM_CODE']
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')


# 测试结果上传
def TestUpload(params,data):
    url = "http://192.168.66.201:9015/mc/http/interface.ms?model=CheckAndSaveTuYaTestSN&method=exeFunc"
    keys_to_check = ['fix_id','dut_order_code','is_misdetect','dut_number_value','token','dut_number_name','elapsed','retry_cnt','station','model','is_pass','user','pc_mac']
    if all(key in params for key in keys_to_check):
        url = url + "&" + "&".join([f"{key}={value}" for key, value in params.items()])
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')

# 工序获取(**换成新的接口：制令单工序查询)
def ProcessGet(data):
    url = "http://192.168.66.200:8015/mc/http/interface.ms?model=getData&method=exeFunc"
    keys_to_check = ['INTERFACENO','INTERFACEDATA']
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')
    
# 涂鸦测试数据获取
def TuyaDataGet(data):
    url = "http://192.168.66.200:8015/mc/http/interface.ms?model=GetTuYaTestParameInfo&method=exeFunc"
    keys_to_check = ['ProductID','ProcessID']
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')  

# 制令单工序查询
def GetGroupInfo(data):
    url = "http://192.168.66.200:8015/mc/http/interface.ms?model=GetGroupInfo&method=exeFunc"
    keys_to_check = ['M_MO_NUMBER']
    if all(key in data for key in keys_to_check):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                return json_data
            else:
                print("请求失败，状态码：", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("请求异常：", e)
    else:
        print('参数有误！')


# 通过mes接口进行用户校验
def login_check(username, password):
    url = 'http://192.168.66.200:8015/mc/http/interface.ms'
    params = {
    'model': 'checkPwdVal',
    'method': 'checkPwdValFunc',
    'LOGIN_NAME': username,
    'PWD': password
    }
    try:
        response = requests.get(url, params=params)
        result = response.text
        return result
    except requests.exceptions.RequestException as e:
        print("请求异常：", e)


if __name__ == "__main__":
    # 登录
    username = 'test1'
    password = '12'
    print(login_check(username, password))

    # 获取工序
    # data = {'INTERFACENO':'001','INTERFACEDATA':'X12312MFG000307-03'}
    # response_data = ProcessGet(data)
    # print(response_data)
    # {'ID': '001', 'Status': '1', 'Message': 'OK:执行成功', 'Data': [{'PM_MO_NUMBER': 'X12310MFG000105-01', 'PM_PROJECT_ID': 'X12310MFG000105', 'PM_AREA_SN': 'SMT-1', 'PM_MODEL_CODE': '2010030325', 'PM_START_GROUP': '投板', 'PM_END_GROUP': '炉后AOI', 'PM_TARGET_QTY': 500, 'PM_INPUT_COUNT': 466, 'PM_FINISH_COUNT': 504}]}
    # {'ID': '001', 'Status': '1', 'Message': 'OK:执行成功', 'Data': [{'PM_MO_NUMBER': 'X12306MFG001229-02', 'PM_PROJECT_ID': 'X12306MFG001229', 'PM_AREA_SN': 'GMCS2', 'PM_MODEL_CODE': '2010100409', 'PM_START_GROUP': '工模测试', 'PM_END_GROUP': '工模测试', 'PM_TARGET_QTY': 50, 'PM_INPUT_COUNT': 1, 'PM_FINISH_COUNT': 1}]}

    # 制令单工序查询(和获取工序002一样，002不用)
    # data = {"M_MO_NUMBER":"X12306MFG001229-02"}
    # response_data = GetGroupInfo(data)
    # print(response_data)
    # {'MSG': '获取数据成功', 'RES': 'OK', 'DETAIL': [{'CRC_GROUP_CODE': 'SMT1', 'GROUP_NAME': '投板', 'CA_ID': 'SMT1-1'}, {'CRC_GROUP_CODE': 'SMT7', 'GROUP_NAME': '炉后AOI', 'CA_ID': 'SMT1-7'}]}
    # {'MSG': '获取数据成功', 'RES': 'OK', 'DETAIL': [{'CA_ID': 'GMCS2-0', 'PMO_AREA_SN': 'GMCS2', 'GROUP_NAME': '工模测试'}]}
    # 涂鸦测试数据获取
    # data = {"ProductID":"2010100409","ProcessID":"GMCS"}
    # response_data = TuyaDataGet(data)
    # data = response_data['data']
    # if data != '':
    #     data = data.lstrip('\ufeff')
    #     pattern = r',\r\n\s*}'
    #     replacement = "\r\n    }"
    #     data = re.sub(pattern, replacement, data)
    #     file_path = "file.json"  # 替换为你想要保存文件的路径和名称
    #     with open(file_path, "w", encoding="utf-8") as file:
    #         file.write(data)
    #     print('获取json文件成功')
    # else:
    #     print('获取失败')

    # 流程校验
    # data = {"M_EMP_NO":"MES","M_GROUP_NAME":"PCBA测试","M_SN":"SNKEL23NV00908","M_MO_NUMBER":"X12312MFG000307-03"}
    # response_data = ProductCheck(data)
    # print(response_data)
    # print(response_data['MSG'][:10])
    # {'MSG': '验证成功', 'GROUP_NAME': '工模测试', 'RES': 'OK', 'MO_NUMBER': 'X12306MFG001229-02'}
    # {'MSG': 'NG:当前工序已过站，请勿重复过站GMCS5-0##0&', 'GROUP_NAME': '工模测试', 'RES': 'NG', 'MO_NUMBER': 'X12310MFG000383-04'} 

    # 过站数据保存
    # data = {"M_EMP_NO":"MES","M_GROUP_NAME":"PCBA测试","M_SN":"SNKEL23NV00908","M_MO_NUMBER":"X12312MFG000307-03"}
    # response_data = ProductStation(data)
    # print(response_data)
    # {'MSG': '过站成功|TEST0000000000', 'GROUP_NAME': '工模测试', 'RES': 'OK', 'MO_NUMBER': 'X12306MFG001229-02'}
    # {'MSG': '过站失败|GTEEJ23KD00DCE|返回结果：NG:当前工序已过站，请勿重复过站GMCS5-0##0&##0&', 'GROUP_NAME': '工模测试', 'RES': 'NG', 'MO_NUMBER': 'X12310MFG000383-04'}
    
    # 产测请求
    # data_time = getTime()
    # data = {"projectid": "X12306MFG001229","itemcode": "2010030325","prodection": "工模测试","paramtype": "SN", "dateflag": data_time }
    # response_data = n2TestRequest(data)
    # print(response_data)
    # {'ID': '1698277840', 'Status': 'OK', 'Message': 'OK:执行成功', 'Data': [{'ID': '77ee3dfb2e9d49b491de76002df919bc', 'PP_PARAM_VAL': '20230824090220230824145200000017', 'PP_SY_NUM': 1, 'PP_NUM_ONE': 1}]}

    # 测试结果上传
    # data_time = getTime() # 获取时间戳
    # mac = '-'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,6)][::-1]) # 获取MAC地址
    # params = {
    #     "fix_id": "firstTest",
    #     "dut_order_code": "X12306MFG001229-02", 
    #     "is_misdetect": "False",
    #     "dut_number_value": 'TEST0000000001',
    #     "token": data_time,
    #     "dut_number_name": "SN",
    #     "elapsed": "50", 
    #     "retry_cnt": "1",
    #     "station": "工模测试", 
    #     "model": "WBR3", 
    #     "is_pass": "True",
    #     "user": "hzzk-kh98", 
    #     "pc_mac": mac
    # }
    # data = {'cases': 
    #         [{'name': '建立连接', 'value': None, 'elapsed': 343, 'result': 'pass'}, 
    #          {'name': '进入测试模式', 'value': None, 'elapsed': 3, 'result': 'pass'}, 
    #          {'name': '图像预览', 'value': None, 'elapsed': 1361, 'result': 'pass'}, 
    #          {'name': '图像测试', 'value': None, 'elapsed': 3388, 'result': 'pass'}, 
    #          {'name': '按键测试', 'value': None, 'elapsed': 2422, 'result': 'pass'}, 
    #          {'name': '喇叭测试', 'value': None, 'elapsed': 1805, 'result': 'pass'}, 
    #          {'name': '麦克风测试', 'value': None, 'elapsed': 9072, 'result': 'pass'}, 
    #          {'name': '指示灯测试', 'value': None, 'elapsed': 4008, 'result': 'pass'}, 
    #          {'name': '红外灯测试', 'value': None, 'elapsed': 3025, 'result': 'pass'}, 
    #          {'name': 'IRCut测试', 'value': None, 'elapsed': 4156, 'result': 'pass'}
    #     ]
    # }
    # response_data= TestUpload(params,data)
    # print(response_data)
    # {'resultCode': '0', 'resultMsg': 'OK:产品SN过站成功##1&&X12210MFG000054-01,MES'}
    # {'resultCode': '0', 'resultMsg': 'NG:当前涂鸦工单【X12306MFG001229-02】工序【工模测试】未获取到MES制令单！'}

    # 产测返回
    # data_time = getTime()
    # data = {"res":"OK","dateflag":getTime(),"id":"77ee3dfb2e9d49b491de76002df919bc","itemsn":"20230824090220230824145200000017"}
    # response_data = n2TestResult(data)
    # {'ID': '1698277927', 'Status': 'OK', 'Message': 'OK:执行成功', 'Data': '1698277927'}


    # 生产过站(不用)
    # data = {"EMP_NO":"ch","WORK_STATION":"ZZCJ9-2","M_SN":"FYWEK21NV003E8","M_RES":"PASS","M_EC_STR":""}
    # response_data = n2ProductionPass(data)
    # print(response_data)
    # "WORK_STATION":"SMT5-1-A"：{'Status': 'NG', 'Message': '产品条码长度不符或者产品未投入##0&##0&'}

    # 获取固件URL
    # data = {"PROJECT_ID":"X12307MFG000575","GROUP_CODE":"DIP2","ITEM_CODE":"9010010174"}
    # response_data = n2GetBurnUrl(data)

    # if response_data is not None:
    #     print(response_data)


