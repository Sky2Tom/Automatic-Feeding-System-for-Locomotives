original_string = "57AA000300177B22726574223A747275652C2272737369223A2D34307D9857AA0003000D7B22726574223A66616C73657DDD"
first_occurrence = original_string.find("57AA00")  # 找到第一次出现的位置
second_occurrence = original_string.find("57AA00", first_occurrence + 1)  # 找到第二次出现的位置

if second_occurrence != -1:  # 如果找到第二次出现的位置
    result_string = original_string[:second_occurrence]  # 截取第二次出现之前的部分
    print(result_string)
else:
    print("未找到第二个'57AA00'")
