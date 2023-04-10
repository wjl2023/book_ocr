import os
import cv2
from PIL import Image
from paddleocr import PPStructure, save_structure_res, draw_structure_result
from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx

# 中文测试图
table_engine = PPStructure(recovery=True)
# 英文测试图
# table_engine = PPStructure(recovery=True, lang='en')

save_folder = './output'
img_path = './images/output_19.png'
img = cv2.imread(img_path)
result = table_engine(img)
save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])
for line in result:
    line.pop('img')
    print(line)

font_path = '/Users/liweijia/Documents/project/ocr/PaddleOCR/PaddleOCR/doc/fonts/simfang.ttf' # PaddleOCR下提供字体包
image = Image.open(img_path).convert('RGB')
im_show = draw_structure_result(image, result, font_path=font_path)
im_show = Image.fromarray(im_show)
im_show.save('result.jpg')