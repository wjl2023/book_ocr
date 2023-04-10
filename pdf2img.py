import os.path

from pdf2image import convert_from_path

pdf_path = './learn_ocr/pdf/1.pdf'
output_dir = './learn_ocr'

images = convert_from_path(pdf_path)

for i,image in enumerate(images):
    filename = f"output_{i+1}.png"
    output_path = os.path.join(output_dir, filename)
    image.save(output_path, 'PNG')