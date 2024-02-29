import fitz
from PIL import Image
import cv2
import numpy as np
import time
import uuid

input_pdf = "teste.pdf"
output_name = "output.jpg"

def main():
    generate_jpg()
    encontrar_aparicoes(output_name, './assets/mobile.jpg')
    encontrar_aparicoes(output_name, './assets/online.jpg')

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
    print('chegou')
    # Carregar as imagens
    img_grande = cv2.imread(imagem_grande)
    img_pequena = cv2.imread(imagem_pequena,  cv2.IMREAD_GRAYSCALE)
    img_gray = cv2.cvtColor (img_grande, cv2.COLOR_BGR2GRAY)

    # Encontrar correspondências usando a correspondência de características
    resultado = cv2.matchTemplate(img_gray, img_pequena, cv2.TM_CCOEFF_NORMED)
    loc = np.where(resultado >= 0.9)  # 0.7 é o limiar de correspondência
    # Desenhar retângulos ao redor das correspondências encontradas
    for pt in zip(*loc[::-1]):
        #cv2.rectangle(img_grande, pt, (pt[0] + 1000, pt[1] + 90), (0, 255, 0), 1)
        crop_img = img_grande[pt[1]:pt[1]+90, pt[0]:pt[0]+1000, :] 
        cv2.imwrite('./temp/'+str(uuid.uuid4().hex)+'.jpg', crop_img)

    # Exibir a imagem resultante
    cv2.imwrite(imagem_grande, img_grande)         
    time.sleep(1)

main()