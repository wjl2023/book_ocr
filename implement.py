import cv2
from paddleocr import PPStructure
from paddleocr import PaddleOCR
from ocr_functions import adjust_bbox_and_read, get_title_style, n_new_result, get_width_and_height, n_clean_title,\
    n_paragraph_split, pd_is_new_paragrph, read, new_result, cut_figure, cut_table, cut_euqation
from my_classes import paragraph
import json

title_1 = "第1章"
title_2 = "1.1知识图谱的基本概念"
title_3 = "1.1.1知识图谱的狭义概念"
# pdf_path = ''

# pdf2img(pdf_path)
table_engine = PPStructure(recovery=True)
ocr = PaddleOCR()
document = paragraph()

width, height = get_width_and_height('./images/output_1.png')
title1, title2, title3 = get_title_style(table_engine, ocr, width,
                                         title_1,
                                         title_2,
                                         title_3,
                                         "./images/output_")

id_count = 0
paragraph_count = 0
title_level_1 = -1
title_level_2 = -1
title_level_3 = -1
last_title = -1
last_figure_name = ''
# aa = 0
# cc = 0

for i in range(514):
    filename = './images/output_' + str(i + 1) + '.png'
    img = cv2.imread(filename)
    origin_result = table_engine(img)
    new = new_result(origin_result, title1, title2, title3)
    last_left = 1000
    last_right = 0
    for line in new:
        #*************************************************************
        #标题检测
        title_text = adjust_bbox_and_read(line, ocr, img, width, title1, title2, title3)
        new_t_text = n_clean_title(line, title_text)
        with open('./title.txt', 'a') as fa:
            if title_text!='':
                fa.write(new_t_text+'\n')

        if new_t_text != '':
            id_count = id_count + 1
            paragraph_count = paragraph_count + 1
            title_level = title_text[2]
            last_title = id_count
            if title_level == '1':
                document.add_paragraph(id_count, paragraph_count, -1, 'title', new_t_text,i)
                title_level_1 = id_count
            if title_level == '2':
                document.add_paragraph(id_count, paragraph_count, title_level_1, 'title', new_t_text,i)
                title_level_2 = id_count
            if title_level == '3':
                document.add_paragraph(id_count, paragraph_count, title_level_2, 'title', new_t_text,i)
                title_level_3 = id_count
        #*************************************************************
        paragraph_count, id_count = cut_euqation(line, img, ocr, width, height, './equation/', document, i, paragraph_count, id_count, last_title)
        #*************************************************************
        #文本检测
        if line.get('type') == 'text':
            new_bbox = []
            bbox = line.get('bbox')
            line['bbox'] = bbox
            region = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]

            # filename_img = './temp/o_' + str(aa) + '.jpg'
            # aa = aa + 1
            # cv2.imwrite(filename_img, region)

            paragraph_new_bbox = n_paragraph_split(region, 35, bbox)
            for bbox in paragraph_new_bbox:
                bbox[0] = min(bbox[0], last_left)
                bbox[2] = max(bbox[2], last_right)
                last_left = bbox[0]
                last_right = bbox[2]
                img_paragraph = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]

                # filename_img = './temp/n_' + str(cc) + '.jpg'
                # cc = cc + 1
                # cv2.imwrite(filename_img, img_paragraph)

                read_t = ocr.ocr(img_paragraph, cls=True)
                read_text = read(read_t)
                if read_text != '':
                    pd = pd_is_new_paragrph(img, bbox)
                    id_count = id_count + 1
                    if pd==1:
                        paragraph_count = paragraph_count + 1
                        document.add_paragraph(id_count, paragraph_count, last_title, 'text', read_text, i)
                    else:
                        document.add_paragraph(id_count, paragraph_count, last_title, 'text', read_text, i)
        #**********************************************************
        #图片识别保存
        elif line.get('type') == 'figure':
            id_count, paragraph_count = cut_figure(line, img, ocr, width, height, './figure/', document, i, paragraph_count, id_count, last_title)
        #**********************************************************
        elif line.get('type') == 'table':
            id_count, paragraph_count, last_figure_name = cut_table(line, img, ocr, width, height, './table/', document, i, paragraph_count, id_count, last_title, last_figure_name)

with open("./huhu.json", "w", encoding="utf-8") as fd:
    for item in document.paragraphs:
        fd.write(json.dumps(item, ensure_ascii=False) + "\n")






