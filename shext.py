from paddleocr import PaddleOCR
import cv2
import re
import numpy as np

# 初始化OCR模型，使用英文识别
ocr = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=True, use_doc_unwarping=False , use_doc_orientation_classify=False)

# 打开摄像头
cap = cv2.VideoCapture(0)

# 设置摄像头分辨率（可选）
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("开始实时OCR识别，按'q'退出")

while True:
    # 读取一帧
    ret, frame = cap.read()
    if not ret:
        print("无法获取摄像头画面")
        break

    # 将BGR图像转换为RGB（PaddleOCR需要RGB格式）
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 执行OCR识别
    result = ocr.ocr(rgb_frame, cls=False)

    # 提取所有识别结果中的文本和置信度
    filtered_texts = []
    if result and result[0]:
        for line in result[0]:
            if line and len(line) >= 2:
                # PaddleOCR返回格式: [[[坐标], ('文本', 置信度)], ...]
                text_info = line[1]
                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                    texta = text_info[0]  # 提取文本
                    confidence = text_info[1]  # 提取置信度
                    # 检查置信度≥0.7
                    if confidence >= 0.7:
                        filtered_texts.append(texta)

    # 如果有识别到的数字，打印出来
    if filtered_texts:
        final_result = "".join(filtered_texts)
        print(f"识别到的数字: {final_result}")
        if final_result == 'C64':
            print("车厢信息：120,240,15,20,17")

    # 在画面上显示识别结果（可选）
    display_frame = frame.copy()
    cv2.putText(display_frame, f"Numbers: {''.join(filtered_texts)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 显示画面
    cv2.imshow('OCR Capture', display_frame)

    # 按'q'退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()