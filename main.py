import fitz
from PIL import Image
import cv2
import numpy as np
import time
import uuid
import pytesseract
import os
import json
import re

temp_dir = './temp/'
input_pdf = "teste.pdf"
output_name = "output.jpg"
date_pattern = re.compile(r'^(0[1-9]|[1-2][0-9]|3[0-1])/(0[1-9]|1[0-2])$')
array_final = []

def main():
    clear_directory(temp_dir)
    generate_jpg()
    encontrar_aparicoes(output_name, './assets/mobile.jpg')
    encontrar_aparicoes(output_name, './assets/online.jpg')
    json_from_array = json.dumps(array_final)
    print(json_from_array)

def generate_jpg():
    compression = 'zip'  # "zip", "lzw", "group4" - need binarized image...

    zoom = 5
    mat = fitz.Matrix(zoom, zoom)

    doc = fitz.open(input_pdf)
    image_list = []

    # Obtém a largura máxima das páginas
    max_width = int(max(page.rect.width for page in doc)) * zoom
    max_height = int(sum(page.rect.height for page in doc)) * zoom

    # Cria uma nova imagem com a largura máxima e altura total das páginas
    final_image = Image.new('RGB', (max_width, max_height), (255, 255, 255))

    # Posição inicial para colar as páginas
    y_offset = 0

    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Cole a imagem na posição atual
        final_image.paste(img, (0, y_offset))
        
        # Atualize a posição para a próxima página
        y_offset += pix.height

    # Salva a imagem final
    final_image.save(output_name, compression=compression)

    # Fecha o arquivo PDF
    doc.close()

def encontrar_aparicoes(imagem_grande, imagem_pequena):
    # Carregar as imagens
    cv2_image_main = cv2.imread(imagem_grande)
    cv2_image_icon = cv2.imread(imagem_pequena)

    # Encontrar correspondências usando a correspondência de características
    resultado = cv2.matchTemplate(cv2_image_main, cv2_image_icon, cv2.TM_CCOEFF_NORMED)
    loc = np.where(resultado >= 0.95)  # 0.7 é o limiar de correspondência
    # Desenhar retângulos ao redor das correspondências encontradas
    for pt in zip(*loc[::-1]):
        temp_name_prefix = temp_dir+str(uuid.uuid4().hex)        
        image_date = temp_name_prefix+'-date.jpg'
        image_title = temp_name_prefix+'-title.jpg'
        image_group = temp_name_prefix+'-group.jpg'
        image_value = temp_name_prefix+'-value.jpg'

        cv2_image_date = cv2_image_main[pt[1]:pt[1]+50, pt[0]+50:pt[0]+160, :] 
        cv2.imwrite(image_date, cv2_image_date)
        
        cv2_image_title = cv2_image_main[pt[1]:pt[1]+50, pt[0]+180:pt[0]+800, :] 
        cv2.imwrite(image_title, cv2_image_title)        

        cv2_image_group = cv2_image_main[pt[1]+50:pt[1]+100, pt[0]+180:pt[0]+800, :] 
        cv2.imwrite(image_group, cv2_image_group)               

        cv2_image_value = cv2_image_main[pt[1]:pt[1]+50, pt[0]+850:pt[0]+1000, :] 
        cv2.imwrite(image_value, cv2_image_value) 
        
        tesseract_response_date = text_corretion(pytesseract.image_to_string(Image.open(image_date), lang="por"))
        tesseract_response_title = text_corretion(pytesseract.image_to_string(Image.open(image_title), lang="por"))
        tesseract_response_group = text_corretion(pytesseract.image_to_string(Image.open(image_group), lang="por"))
        tesseract_response_value = text_corretion(pytesseract.image_to_string(Image.open(image_value), lang="eng"))
        print(temp_name_prefix, tesseract_response_value)

        if tesseract_response_date == "" or not date_pattern.match(tesseract_response_date):
            continue

        new_data = {
            "date": tesseract_response_date, 
            "title": tesseract_response_title,
            "group": tesseract_response_group,
            "value": tesseract_response_value,
        }
        array_final.append(new_data)

    # Exibir a imagem resultante
    cv2.imwrite(imagem_grande, cv2_image_main)         
    time.sleep(1)


def text_corretion(text):
    text = text.strip()
    text = text.replace("\r","")
    text = text.replace("\n","")
    text = text.replace("   "," ")
    text = text.replace("  "," ")
    return text

def clear_directory(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"The directory '{directory_path}' does not exist.")
        return

    # Get a list of all files in the directory
    files = os.listdir(directory_path)

    # Iterate over each file and remove it
    for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            elif os.path.isdir(file_path):
                # If you want to clear subdirectories as well, uncomment the line below
                # shutil.rmtree(file_path)
                print(f"Skipped (subdirectory): {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print(f"The directory '{directory_path}' has been cleared.")

main()