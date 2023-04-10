from paddleocr import PaddleOCR
import cv2

ocr = PaddleOCR()
img_path = './images/output_19.png'
bbox = [297, 750, 848, 781]
img_origin = cv2.imread(img_path)
img_next = img_origin[bbox[1]-20:bbox[3]+20, 0:1500]
cv2.imshow('img_next', img_next)
result = ocr.ocr(img_next, cls=True)
for line in result:
    print(line)
cv2.waitKey(0)