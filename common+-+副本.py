# import pandas as pd
# import os
# from PIL import Image
#
# # 配置路径
# excel_file = 'train_label.xlsx'
# image_folder = r'D:\zhifubao\附件1-铁路货运列车车号识别数据集\train'  # 替换为你的图片文件夹路径
# output_folder = 'labels'  # 标签输出文件夹
#
# # 创建输出文件夹
# os.makedirs(output_folder, exist_ok=True)
#
# # 读取Excel文件
# df = pd.read_excel(excel_file, sheet_name='Sheet1')
#
# # 处理每一行数据
# for _, row in df.iterrows():
#     # 获取图片编号
#     img_id = str(int(row['NO.']))
#
#     # 构建图片路径
#     img_path = os.path.join(image_folder, f"{img_id}.jpg")
#
#     # 获取图片尺寸
#     try:
#         with Image.open(img_path) as img:
#             img_width, img_height = img.size
#     except FileNotFoundError:
#         print(f"警告: 图片 {img_id}.jpg 未找到，跳过处理")
#         continue
#
#     # 解析坐标
#     try:
#         # 处理Top Left坐标
#         tl_parts = str(row['Top Left']).split(',')
#         x1 = int(tl_parts[0].strip())
#         y1 = int(tl_parts[1].strip())
#
#         # 处理Lower Right坐标
#         br_parts = str(row['Lower right']).split(',')
#         x2 = int(br_parts[0].strip())
#         y2 = int(br_parts[1].strip())
#     except (ValueError, IndexError):
#         print(f"警告: 行 {row['NO.']} 的坐标格式错误，跳过处理")
#         continue
#
#     # 计算YOLOv5格式的归一化坐标
#     x_center = (x1 + x2) / 2.0 / img_width
#     y_center = (y1 + y2) / 2.0 / img_height
#     width = (x2 - x1) / img_width
#     height = (y2 - y1) / img_height
#
#     # 确保坐标在0-1范围内
#     x_center = max(0, min(1, x_center))
#     y_center = max(0, min(1, y_center))
#     width = max(0, min(1, width))
#     height = max(0, min(1, height))
#
#     # 创建标签文件
#     label_file = os.path.join(output_folder, f"{img_id}.txt")
#     with open(label_file, 'w') as f:
#         f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
#
# print("标签生成完成！")

# # 生成图片路径列表
# output_file = 'image_paths.txt'
# base_path = './images/train/'
# total_images = 500  # 从1到400
#
# with open(output_file, 'w') as f:
#     for i in range(1, total_images + 1):
#         f.write(f"{base_path}{i}.jpg\n")
# 
# print(f"图片路径列表已保存到 {output_file}")
import time
#

#
# # 在这里放置你想要测试的代码
# for i in range(0, 1000000):
#     pass
#

#



from paddleocr import PaddleOCR
import paddleocr
# 1. 初始化OCR模型
# use_angle_cls=True 用于启用方向分类（识别横屏/竖屏）
# lang='ch' 表示使用中文模型， 'en' 为英文， 可切换为 'chinese_cht‘（繁体）、’ko‘、’ja‘等
ocr = PaddleOCR(use_angle_cls=True, lang='en')
start_time = time.time()  # 获取当前时间
# 2. 指定图片路径
img_path = '2.jpg'  # 替换为你的图片路径

# 3. 执行OCR识别
result = ocr.ocr(img_path)

end_time = time.time()  # 代码运行后再次获取当前时间
execution_time = end_time - start_time  # 计算运行时间
#


print(f"代码运行时间: {execution_time}秒")
# 4. 打印并可视化结果
# Result是一个列表，每个元素对应一行文字，包含了文本框坐标、文字内容和置信度
for line in result:
    print(line)

# 可选：使用自带工具绘制结果
# from PIL import Image
# image = Image.open(img_path).convert('RGB')
# boxes = [line[0] for line in result]
# txts = [line[1][0] for line in result]
# scores = [line[1][1] for line in result]
# im_show = draw_ocr(image, boxes, txts, scores)
# im_show = Image.fromarray(im_show)
# im_show.save('result.jpg')  # 保存识别结果图片

# import easyocr
# reader = easyocr.Reader(['ch_sim','en']) # 指定中文和英文
# result = reader.readtext('111.jpg')
# for detection in result:
#     print(detection[1]) # 打印识别到的文本

# from paddleocr import PaddleOCR
# import re
#
# # 初始化OCR模型，使用英文识别
# ocr = PaddleOCR(use_angle_cls=True, lang='en')
#
# # 指定图片路径
# img_path = '1.jpg'
#
# # 执行OCR识别
# result = ocr.ocr(img_path)
#
# # 提取所有识别结果中的文本和置信度
# filtered_texts = []
# for line in result:
#     if line:  # 确保行不为空
#         text = line["rec_texts"]
#         con = line["rec_scores"]
#         for i, confidence in enumerate(con):
#             texta = text[i]  # 提取文本
#             # 检查置信度≥0.7且文本为纯数字
#             if confidence >= 0.7 and re.fullmatch(r'\d+', texta):
#                 filtered_texts.append(texta)
# print(filtered_texts)
#
#
# # 拼接所有符合条件的数字字符串
# final_result = ''.join(filtered_texts)
# print(final_result)