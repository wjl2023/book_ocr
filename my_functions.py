from PIL import Image, ImageOps
import os
import cv2


def get_bbox_width(bbox):
    y_min = bbox[1]
    y_max = bbox[3]
    width = y_max - y_min
    return width


def wait_to_finish():
    pass


def merge_img_2(img_path1, img_path2, save_path, width, fill):
    img1 = Image.open(img_path1)
    img2 = Image.open(img_path2)
    width1, height1 = img1.size
    width2, height2 = img2.size
    height = height1 + height2 + fill

    # 将图片 mode 转为 RGB 模式
    img1 = img1.convert('RGB')
    img2 = img2.convert('RGB')

    # 创建一个新的白色底图，大小为合并后图片的尺寸
    new_img = Image.new('RGB', (width, height), color='white')

    # 在底图上粘贴 img1 和 img2
    new_img.paste(img1, box=(0, 0))
    new_img.paste(img2, box=(0, height1 + fill))

    # 保存合并后的图片
    new_img.save(save_path)


def new_result(result):
    new = {}
    for line in result:
        line.pop('img')
        line_start = line.get('bbox')[1]
        line['start'] = line_start
        if line.get('type') == 'title':
            bbox = line.get('bbox')
            bbox_width = get_bbox_width(bbox)
            if bbox_width <= 30:
                line['type'] = 'text'
    new = sorted(result, key=lambda x: x['start'])
    return new


def title_scan(line, title, flag):
    new_title = title
    res_value = line.get('res')
    bbox = line.get('bbox')
    width = get_bbox_width(bbox)
    if 29 < width < 35:
        flag = 0
        new_title = ''
        for element in res_value:
            confidence = round(element['confidence'], 2)
            if confidence > 0.7:
                new_title = new_title + element['text']

    return new_title, flag


def text_scan(line, title, img_to_crop, width, flag):
    type_s = line.get('type')
    if type_s != 'header' and type_s != 'footer' and type_s != 'reference':
        print(line.get('type'))
        bbox = line.get('bbox')
        cropped_text = img_to_crop.crop(bbox)
        target_length = bbox[3] - bbox[1]
        target_width = width
        delta_width = target_width - cropped_text.size[0]
        pad_width = delta_width / 2
        padded_img = ImageOps.expand(cropped_text, (int(pad_width), 0, (delta_width - int(pad_width)), 0), fill='white')
        padded_img.save('./temp.png')
        if flag is 0:
            save_path = './out_img/' + title + '.png'
            padded_img.save(save_path)
            os.remove('./temp.png')
        else:
            old_path = './out_img/' + title + '.png'
            merge_img_2(old_path, './temp.png', old_path, width, 20)
        flag = 1
    return flag



def get_text(line, title):
    type_s = line.get('type')
    res_value = line.get('res')
    text_s = ''
    if type_s == 'text':
        for element in res_value:
            text_s = text_s + element['text']
        # if flag is 0:
        filename = './txt1/' + str(title[5:]) + '.txt'
        if text_s != '':
            with open(filename, 'a') as file:
                file.write(text_s + '\n')


def adjust_bbox_and_read(line, ocr, img, width, title1, title2, title3):
    old_bbox = line.get('bbox')
    old_bbox_width = get_bbox_width(old_bbox)
    #ocr = Paddleocr()
    title_text = ''
    if title1[0] <= old_bbox_width <= title1[1]:
        fill = 15
        img_title = img[old_bbox[1] - fill:old_bbox[3] + fill, 0:width]
        title_result = ocr.ocr(img_title, cls=True)
        title_text = 'ti1: '
        for title_line in title_result:
            for item in title_line:
                if isinstance(item, list):
                    title_text += item[1][0]
                elif isinstance(item, tuple):
                    title_text += item[0]
        print(title_text)
    elif title2[0] <= old_bbox_width <= title2[1]:
        fill = 15
        img_title = img[old_bbox[1] - fill:old_bbox[3] + fill, 0:width]
        title_result = ocr.ocr(img_title, cls=True)
        title_text = 'ti2: '
        for title_line in title_result:
            for item in title_line:
                if isinstance(item, list):
                    title_text += item[1][0]
                elif isinstance(item, tuple):
                    title_text += item[0]
        print(title_text)
    elif title3[0] <= old_bbox_width <= title3[1]:
        fill = int(old_bbox_width / 2)
        img_title = img[old_bbox[1]-fill:old_bbox[3]+fill, 0:width]
        title_result = ocr.ocr(img_title, cls=True)
        title_text = 'ti3: '
        for title_line in title_result:
            for item in title_line:
                if isinstance(item, list):
                    title_text += item[1][0]
                elif isinstance(item, tuple):
                    title_text += item[0]
        print(title_text)
    return title_text


def cut_figure(line, img, ocr, width, length, path, title):
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
            if figure_capture_text[0] == '图':
                cv2.imwrite(filename, new_img)

            filename1 = './txt1/' + str(title[5:]) + '.txt'
            if figure_capture_text != '':
                with open(filename1, 'a') as file:
                    file.write("here's a figure:" + figure_capture_text + '\n')


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
                print(title_text)                
                if title_text == input_title_1:
                    title_width = get_bbox_width(bbox_origin)
                    expected_title1 = [title_width - 10, title_width + 10]
                if title_text == input_title_2:
                    title_width = get_bbox_width(bbox_origin)
                    expected_title2 = [title_width - 5, title_width + 5]
                if title_text == input_title_3:
                    title_width = get_bbox_width(bbox_origin)
                    expected_title3 = [title_width - 2, title_width + 2]
                    if expected_title3[1] > expected_title2[0]:
                        expected_title2[0] = expected_title3[1] + 1
                    flag = True
                    break
            if flag:
                break
        if flag:
            break
    return expected_title1, expected_title2, expected_title3