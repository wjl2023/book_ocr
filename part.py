import cv2
from PIL import Image, ImageOps
from paddleocr import PPStructure
from my_functions import new_result, get_text, adjust_bbox_and_read, cut_figure, get_title_style
from paddleocr import PaddleOCR

# 中文测试图
table_engine = PPStructure(recovery=True)
ocr = PaddleOCR()
# 英文测试图
# table_engine = PPStructure(recovery=True, lang='en')

save_folder = './output'

cnt = 0
flag = 0
title = '0'
img_to_crop = Image.open('./learn_ocr/output_1.png')
width, length = img_to_crop.size

title1, title2, title3 = get_title_style(table_engine, ocr, width, "", "2.1关于本书", "2.1.1内容和结构",
                                         './learn_ocr/output_')
print(title1)
print(title2)
print(title3)
for i in range(220):
    filename = './learn_ocr/output_' + str(i + 1) + '.png'
    img = cv2.imread(filename)
    result = table_engine(img)
    new = new_result(result)

    #*****************************************************
    # for line in result:
    #     print(line.get('type'))
    #     cut_figure(line, img, ocr, 1500, './figure_imgs/')
    # print('**********************')
    # for line in new:
    #     print(line.get('type'))

    #********************************************************
    for line in new:
        new_text = ''
        if line.get('type') == 'title':
            new_text = adjust_bbox_and_read(line, ocr, img, width, title1, title2, title3)
            if new_text != '':
                print(new_text)
                with open('./titles/title_1.txt', 'a') as title_file:
                    title_file.write(new_text + '\n')
        # else:
        #     get_text(line, title)
        #     cut_figure(line, img, ocr, width, length, './figure_imgs/', title)


# for line in result:
#     line.pop('img')
    # if line.get('type') == 'text':
    #     bbox = line.get('bbox')
    #     cropped_text = img_to_crop.crop(bbox)
    #     target_width = width
    #     target_length = bbox[3] - bbox[1]
    #     print('target_length:', target_length)
    #     print('target_width:', target_width)
    #     delta_width = target_width - cropped_text.size[0]
    #     pad_width = delta_width / 2
    #     padded_img = ImageOps.expand(cropped_text, (int(pad_width), 0, (delta_width - int(pad_width)), 0), fill='white')
    #     cropped_name = './cropped_text_{}.png'.format(cnt)
    #     cnt = cnt + 1
    #     padded_img.save(cropped_name)

    # if line.get('type') == 'title':
    #     line_start = line.get('bbox')[1]
    #     print('title: ', line_start)
    # if line.get('type') == 'text':
    #     line_start = line.get('bbox')[1]
    #     print('text: ', line_start)








