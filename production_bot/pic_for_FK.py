# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 13:00:29 2019

@author: alexu
"""

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

# определяете шрифт
font = ImageFont.trueType('/путь/до/файла/со/шрифтом.ttf')

# определяете положение текста на картинке
text_position = (150, 150)

# цвет текста, RGB
text_color = (255,0,0)

# собственно, сам текст
text = 'Фамилия Имя Отчество'

# загружаете фоновое изображение
img = Image.open('blank.jpg')

# определяете объект для рисования
draw = ImageDraw.Draw(img)

# добавляем текст
draw.text(text_position, text, text_color, font)

# сохраняем новое изображение
img.save('blank_with_text.jpg')