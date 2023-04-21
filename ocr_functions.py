from PIL import Image, ImageOps
import cv2
import numpy as np
import os.path
from pdf2image import convert_from_path
from my_classes import chapter


def bbox_expand(bbox):
    new_bbox = [0, 0, 0, 0]
    new_bbox[0] = bbox[0] - 13
    new_bbox[1] = bbox[1] - 13
    new_bbox[2] = bbox[2] + 13
    new_bbox[3] = bbox[3] + 13
    return new_bbox



def read(text):
    new_text = ''
    for line in text:
            for item in line:
                if isinstance(item, list):
                    new_text += item[1][0]
                elif isinstance(item, tuple):
                    new_text += item[0]
    return new_text



def get_bbox_width(bbox):
    y_min = bbox[1]
    y_max = bbox[3]
    width = y_max - y_min
    return width 


def get_width_and_height(img_filename):
    img = cv2.imread(img_filename)
    img_height, img_width = img.shape[:2]
    return img_width, img_height


def new_result(result, title1, title2, title3):
    new = {}
    line_start = 0
    for line in result:
        line.pop('img')
        line_start = line.get('bbox')[1]
        line['start'] = line_start
        if line.get('type') == 'title':
            bbox = line.get('bbox')
            bbox_width = get_bbox_width(bbox)
            if bbox_width <= title3[0] or title3[1]<=bbox_width<=title2[0] or title2[1]<= bbox_width<=title1[0] or bbox_width>=title1[1]:
                line['type'] = 'text'
                
    new = sorted(result, key=lambda x: x['start'])
    return new


def n_new_result(result, title1, title2, title3):
    new = {}
    line_start = 0
    for line in result:
        line.pop('img')
        line_start = line.get('bbox')[1]
        line['start'] = line_start
        if line.get('type') == 'title':
            bbox = line.get('bbox')
            bbox_width = get_bbox_width(bbox)
            if bbox_width <= title3[0] or title3[1]<=bbox_width<=title2[0] or title2[1]<= bbox_width<=title1[0] or bbox_width>=title1[1]:
                line['type'] = 'text'
    new = sorted(result, key=lambda x: x['start'])
    line_start = 0
    line_end = 0
    new_new = []
    for line in new:
        line_start = line.get('bbox')[1]
        if line_start >= line_end:
            if line.get('bbox')[1]<line.get('bbox')[3]:
                line_end = line.get('bbox')[3]
                new_new.append(line)
                new_bbox = bbox_expand(line.get('bbox'))
                line['bbox'] = new_bbox
            # if line.get('type') == 'text':
                # line['bbox'][0] = 0
                # line['bbox'][2] = 1500
        else:
            if line_end+22<line.get('bbox')[3]:
                line_start = line_end + 22
                line_end = line.get('bbox')[3]
                line['bbox'][1] = line_start
                new_new.append(line)
                new_bbox = bbox_expand(line.get('bbox'))
                line['bbox'] = new_bbox
    return new_new


def get_title_style(table_engine, ocr, width, input_title_1, input_title_2, input_title_3, path_filename):
    expected_title1 = [55, 100]
    expected_title2 = [35, 55]
    expected_title3 = [30, 35]
    flag = False
    for i in range(100):
        img_filename = path_filename + str(i + 1) + '.png'
        img = cv2.imread(img_filename)
        result = table_engine(img)
        for line in result:
            if line.get('type') == 'title':
                title_text = ''
                bbox_origin = line.get('bbox')
                new_img = img[bbox_origin[1] - 10:bbox_origin[3] + 10, 0:width]
                title_result = ocr.ocr(new_img, cls=True)
                for title_line in title_result:
                    for item in title_line:
                        if isinstance(item, list):
                            title_text += item[1][0]
                        elif isinstance(item, tuple):
                            title_text += item[0]
                title_text = title_text.replace(" ","")
                # print(title_text)                
                if title_text == input_title_1:
                    title_width = get_bbox_width(bbox_origin)
                    expected_title1 = [title_width - 15, title_width + 15]
                if title_text == input_title_2:
                    title_width = get_bbox_width(bbox_origin)
                    expected_title2 = [title_width - 7, title_width + 7]
                if title_text == input_title_3:
                    title_width = get_bbox_width(bbox_origin)
                    expected_title3 = [title_width - 8, title_width + 4]
                    if expected_title3[1] > expected_title2[0]:
                        expected_title2[0] = expected_title3[1] + 1
                    flag = True
                    break
            if flag:
                break
        if flag:
            break
    return expected_title1, expected_title2, expected_title3


def get_title_text(title_text, title_result):
    new_title_text = title_text
    for title_line in title_result:
            for item in title_line:
                if isinstance(item, list):
                    new_title_text += item[1][0]
                elif isinstance(item, tuple):
                    new_title_text += item[0]
    return new_title_text



def adjust_bbox_and_read(line, ocr, img, width, title1, title2, title3):
    new_title_text = ''
    if line.get('type') == 'title':
        old_bbox = line.get('bbox')
        old_bbox_width = get_bbox_width(old_bbox)
        img_title = img[old_bbox[1]:old_bbox[3], 0:width]
        # cv2.imshow('1', img_title)
        # cv2.waitKey(0)
        if title1[0] <= old_bbox_width <= title1[1]:
            fill = 15
            img_title = img[old_bbox[1] - fill:old_bbox[3] + fill, 0:width]
            title_result = ocr.ocr(img_title, cls=True)
            title_level = 'ti1: '
            new_title_text = get_title_text(title_level, title_result)
            # print(new_title_text)
        elif title2[0] <= old_bbox_width <= title2[1]:
            fill = 15
            img_title = img[old_bbox[1] - fill:old_bbox[3] + fill, 0:width]
            title_result = ocr.ocr(img_title, cls=True)
            title_level = 'ti2: '
            new_title_text = get_title_text(title_level, title_result)
            # print(new_title_text)
        elif title3[0] <= old_bbox_width <= title3[1]:
            fill = int(old_bbox_width / 2)
            img_title = img[old_bbox[1]-fill:old_bbox[3]+fill, 0:width]
            title_result = ocr.ocr(img_title, cls=True)
            title_level = 'ti3: '
            new_title_text = get_title_text(title_level, title_result)
            # print(new_title_text)
    return new_title_text


#这个函数后期还要进行修改，这里只是进行了简单的规则判断进行标题剪枝
def clean_title(line, text):
    t_text = text
    if t_text != '':
        title_level = text[2]
        tt_text = text[5:]
        t_text = tt_text.replace(" ", "")

        if title_level == '1' and len(t_text) > 2:
            if t_text[1].isdigit():
                pass
            else:
                line['type'] = 'text'
        elif title_level == '2' and len(t_text) > 3:
            if t_text[2].isdigit():
                pass
            else:
                line['type'] = 'text'
        elif title_level == '3' and len(t_text) > 5:
            if t_text[4].isdigit():
                pass
            else:
                line['type'] = 'text'
        else:
            line['type'] = 'text'
    if line.get('type') == 'text':
        t_text = ''
    return t_text


def n_clean_title(line, text):
    t_text = text
    if t_text != '':
        title_level = text[2]
        tt_text = text[5:]
        t_text = tt_text.replace(" ", "")

        if title_level == '1' and len(t_text) > 2:
            if t_text[1].isdigit():
                pass
            else:
                line['type'] = 'text'
        elif title_level == '2' and len(t_text) > 3:
            if t_text.count('.') == 1:
                pass
            else:
                line['type'] = 'text'
        elif title_level == '3' and len(t_text) > 5:
            if t_text.count('.') == 2:
                pass
            else:
                line['type'] = 'text'
        else:
            line['type'] = 'text'
    if line.get('type') == 'text':
        t_text = ''
    return t_text



def pd_is_new_paragrph(img, bbox):
    new_bbox = [bbox[0], bbox[1], bbox[0]+60, bbox[1]+40]
    new_img = img[new_bbox[1]:new_bbox[3], new_bbox[0]:new_bbox[2]]
    img_gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
    if np.sum(img_gray[:, :] == 0) >= 10:
        return 0
    else:
        return 1
    


def paragraph_split(input_img, line_space, origin_bbox):
    img_gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    img_height, img_width = img_gray.shape[:2]
    for row in range(img_height):
        if np.sum(img_gray[row, :] == 0) >= 2:
            img_gray[row, :] = 0
    dao = -1
    for row in range(img_height):
        distence = 0
        if row > dao:
            if img_gray[row, 0] == 0:
                if row + line_space < img_height:
                    for new_row in range(line_space):
                        if img_gray[row + new_row, 0] == 0:
                            distence = new_row
                    if distence > line_space-2:
                        img_gray[row:row+distence, :] = 0 
                        dao = row + distence
    # cv2.imshow('2', img_gray)
    # cv2.waitKey(0)
    paragraph_bbox = []
    qishi = 0
    jieshu = 0
    flag = 0
    last_jieshu = 0
    for row in range(img_height):
        if img_gray[row, 0] == 0:
            if flag == 0 and img_gray[min(row+5, img_height-1), 0] == 0:
                qishi = row
            flag = 1
            distence = distence + 1
        else:
            if distence > line_space-20:
                flag = 0
                last_jieshu = jieshu
                jieshu = row
                paragraph_bbox.append([0, max(qishi-10, 0, last_jieshu+8), img_width, min(jieshu+12, img_height)])
            distence = 0
    for bbox in paragraph_bbox:
        bbox[0] = origin_bbox[0] + bbox[0]
        bbox[1] = origin_bbox[1] + bbox[1]
        bbox[2] = origin_bbox[0] + bbox[2]
        bbox[3] = origin_bbox[1] + bbox[3]
    return paragraph_bbox
    # for bbox in paragraph_bbox:
    #     img_paragraph = input_img[bbox[1]:bbox[3], bbox[0]:bbox[2]]
    #     cv2.imshow('1', img_paragraph)
    #     cv2.waitKey(0)

def cut_figure(line, img, ocr, width, length, path, paragraph, i, paragraph_count, id_count, last_title):
    if line.get('type') == 'figure':
        figure_bbox = line.get('bbox')
        if figure_bbox[3]+85 < length:
            new_img = img[figure_bbox[1]:figure_bbox[3], figure_bbox[0]:figure_bbox[2]]
            figure_capture = img[figure_bbox[3]+5:figure_bbox[3]+85, 0:width]
            figure_capture_result = ocr.ocr(figure_capture)
            figure_capture_text = ''
            for figure_capture_line in figure_capture_result:
                for item in figure_capture_line:
                    if isinstance(item, list):
                        figure_capture_text += item[1][0]
                    elif isinstance(item, tuple):
                        figure_capture_text += item[0]
            # print(figure_capture_text)
            filename = path + figure_capture_text + '.jpg'
            if figure_capture_text != '':
                n_figure_capture_text = figure_capture_text.replace(" ", "")
                if n_figure_capture_text[0] == '图':
                    id_count = id_count + 1
                    paragraph_count = paragraph_count + 1
                    cv2.imwrite(filename, new_img)
                    new_text = './figure/' + n_figure_capture_text + '.jpg'
                    paragraph.add_paragraph(id_count, paragraph_count, last_title, 'figure', new_text, i)
    return id_count, paragraph_count


def cut_table(line, img, ocr, width, length, path, paragraph, i, paragraph_count, id_count, last_title, last_figure_name):
    if line.get('type') == 'table':
        table_bbox = line.get('bbox')
        if table_bbox[1] - 50 > 0:
            new_img = img[table_bbox[1]:table_bbox[3], table_bbox[0]:table_bbox[2]]
            table_cap = img[table_bbox[1]-50:table_bbox[1]-5, 0:width]
            table_cap_result = ocr.ocr(table_cap)
            table_cap_text = ''
            for table_line in table_cap_result:
                for item in table_line:
                    if isinstance(item, list):
                        table_cap_text += item[1][0]
                    elif isinstance(item, tuple):
                        table_cap_text += item[0]
            if table_cap_text != '':
                n_table_cap_text = table_cap_text.replace(" ", "")
                if n_table_cap_text[0] == '表':
                    id_count = id_count + 1
                    paragraph_count = paragraph_count + 1
                    new_text = path + n_table_cap_text + '.jpg'
                    cv2.imwrite(new_text, new_img)
                    paragraph.add_paragraph(id_count, paragraph_count, last_title, 'table', new_text, i)
                    last_figure_name = n_table_cap_text
                if n_table_cap_text[0] == '续':
                    id_count = id_count + 1
                    new_text = path + last_figure_name + '_续表.jpg'
                    cv2.imwrite(new_text, new_img)
                    paragraph.add_paragraph(id_count, paragraph_count, last_title, 'table', new_text, i)
    return id_count, paragraph_count, last_figure_name


def cut_euqation(line, img, ocr, width, height, path, paragraph, i, paragraph_count, id_count, last_title):
    paragraph_count_n = paragraph_count
    id_count_n = id_count
    if line.get('type') == 'equation':
        eq_bbox = line.get('bbox')
        new_img = img[max(eq_bbox[1]-20, 0):min(eq_bbox[3]+20, height-1), max(eq_bbox[0]-40, 0):min(eq_bbox[2]+40, width-1)]
        new_ti_img = img[max(eq_bbox[1]-20, 0):min(eq_bbox[3]+20, height-1), min(eq_bbox[2]+40, width-10):width-1]
        eq_result = ocr.ocr(new_ti_img)
        eq_ti_text = ''
        for eq_line in eq_result:
                for item in eq_line:
                    if isinstance(item, list):
                        eq_ti_text += item[1][0]
                    elif isinstance(item, tuple):
                        eq_ti_text += item[0]
        if eq_ti_text != '':
            n_eq_ti_text = eq_ti_text.replace(" ", "")
            filename = path + n_eq_ti_text + '.jpg'
            paragraph_count_n = paragraph_count + 1
            id_count_n = id_count + 1
            cv2.imwrite(filename, new_img)
            paragraph.add_paragraph(id_count_n, paragraph_count_n, last_title, 'equation', filename, i)
        else:
            line['type'] = 'figure'
    return paragraph_count_n, id_count_n
    


def n_paragraph_split(input_img, line_space, origin_bbox):
    n_img_gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    ret, img_gray = cv2.threshold(n_img_gray, 128, 255, cv2.THRESH_BINARY)
    img_height, img_width = img_gray.shape[:2]
    for row in range(img_height):
        if np.sum(img_gray[row, :] == 0) >= 1:
            img_gray[row, :] = 0
    
    # gray_img_name = './temp/tt/' + str(j) + '.jpg'
    # cv2.imwrite(gray_img_name, img_gray)
    # j = j + 1

    dao = -1
    for row in range(img_height):
        distence = 0
        if row > dao:
            if img_gray[row, 0] == 0:
                if row + line_space < img_height:
                    for new_row in range(line_space):
                        if img_gray[row + new_row, 0] == 0:
                            distence = new_row
                    if distence > line_space-2:
                        img_gray[row:row+distence, :] = 0 
                        dao = row + distence
    # cv2.imshow('2', img_gray)
    # cv2.waitKey(0)

    # gray_img_name = './temp/tt/' + str(j) + '.jpg'
    # cv2.imwrite(gray_img_name, img_gray)
    # j = j + 1

    # paragraph_bbox = []
    # qishi = 0
    # jieshu = 0
    # flag = 0
    # last_jieshu = 0
    # for row in range(img_height):
    #     if img_gray[row, 0] == 0:
    #         if flag == 0 and img_gray[min(row+5, img_height-1), 0] == 0:
    #             qishi = row
    #         flag = 1
    #         distence = distence + 1
    #     else:
    #         if distence > line_space-20:
    #             flag = 0
    #             last_jieshu = jieshu
    #             jieshu = row
    #             paragraph_bbox.append([0, max(qishi-10, 0, last_jieshu+8), img_width, min(jieshu+12, img_height)])
    #         distence = 0
    # for bbox in paragraph_bbox:
    #     bbox[0] = origin_bbox[0] + bbox[0]
    #     bbox[1] = origin_bbox[1] + bbox[1]
    #     bbox[2] = origin_bbox[0] + bbox[2]
    #     bbox[3] = origin_bbox[1] + bbox[3]
    paragraph_bbox = []
    length_count = 0
    qishi = 0
    jieshu = 0
    for row in range(img_height):
        if row < img_height - 1:
            if img_gray[row, 0] == 0:
                if length_count == 0:
                    qishi = row
                length_count = length_count + 1
            else :
                if length_count != 0:
                    if length_count > line_space - 20:
                        jieshu = row
                        length_count = 0
                        paragraph_bbox.append([0, qishi, img_width, jieshu])
                else:
                    pass
        elif row == img_height - 1:
            if length_count != 0:
                if length_count > line_space - 20:
                    jieshu = row
                    length_count = 0
                    paragraph_bbox.append([0, qishi, img_width, jieshu])
            else:
                pass
    #段落在原始的图片中的位置
    for bbox in paragraph_bbox:
        bbox[0] = origin_bbox[0] + bbox[0]
        bbox[1] = origin_bbox[1] + bbox[1]
        bbox[2] = origin_bbox[0] + bbox[2]
        bbox[3] = origin_bbox[1] + bbox[3]
    for bbox in paragraph_bbox:
        bbox[0] = bbox[0] - 10
        bbox[1] = bbox[1] - 10
        bbox[2] = bbox[2] + 10
        bbox[3] = bbox[3] + 10
    return paragraph_bbox