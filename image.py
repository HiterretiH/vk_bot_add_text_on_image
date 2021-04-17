import numpy as np
from PIL import Image, ImageFont, ImageDraw
import cv2
import config

font = ImageFont.truetype(config.font_path, size=config.font_size)


def get_text_lines(text, width, draw):
    width = int(width*0.9)
    width1 = int(width*0.95)
    text = text.split('\n')
    res = []

    for line in text:
        arr = line.split()
        while arr:
            left = []
            w, h = draw.textsize(' '.join(arr), font=font)
            while len(arr) > 1 and w > width:
                left.insert(0, arr[-1])
                arr.pop(-1)
                w, h = draw.textsize(' '.join(arr), font=font)
            if len(arr) == 1 and w > width:
                t = list(arr[0])
                arr = []
                while t:
                    a = t[0]
                    t.pop(0)
                    w, h = draw.textsize(a, font=font)
                    while w < width1 and t:
                        a += t[0]
                        t.pop(0)
                        w, h = draw.textsize(a, font=font)
                    res.append(a + ('-' if t else ''))
            else:
                res.append(' '.join(arr))
            arr = left
    w, h = draw.textsize('A', font=font)
    return [res, h]


def drawTextOnImage(file, text=""):
    if len(text) > 100:
        text = text[:100]

    img = cv2.imread(file)


    if max(img.shape[:2]) > 600:
        if img.shape[0] <= img.shape[1]:
            img = cv2.resize(img, (600, int(img.shape[0] * 600/img.shape[1])))
        else:
            img = cv2.resize(img, (int(img.shape[1] * 600 / img.shape[0]), 600))

    elif max(img.shape[:2]) < 450:
        if img.shape[0] >= img.shape[1]:
            img = cv2.resize(img, (450, int(img.shape[0] * 450/img.shape[1])))
        else:
            img = cv2.resize(img, (int(img.shape[1] * 450 / img.shape[0]), 450))

    img = np.concatenate((img, np.ones((1, img.shape[1], 3))*255))

    lines = np.zeros((4, img.shape[1], 3))
    img = np.concatenate((lines, img, lines), axis=0)
    columns = np.zeros((img.shape[0], 4, 3))
    img = np.concatenate((columns, img, columns), axis=1)

    lines = np.empty((4, img.shape[1], 3))
    lines.fill(255)
    img = np.concatenate((lines, img, lines), axis=0)
    columns = np.empty((img.shape[0], 4, 3))
    columns.fill(255)
    img = np.concatenate((columns, img, columns), axis=1)

    img = np.concatenate((np.zeros((25, img.shape[1], 3)), img), axis=0)
    columns = np.zeros((img.shape[0], 48, 3))
    img = np.concatenate((columns, img, columns), axis=1)

    lines, h = get_text_lines(text, img.shape[1], ImageDraw.Draw(Image.fromarray(img.astype(np.uint8))))

    y_pos = img.shape[0]

    img = np.concatenate((img, np.zeros((h*(len(lines)+1), img.shape[1], 3))), axis=0)

    img = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img)

    draw = ImageDraw.Draw(pil_img)

    for i in range(len(lines)):
        w, h = draw.textsize(lines[i], font=font)
        draw.text((int((img.shape[1] - w) / 2), y_pos), lines[i], fill='rgb(255, 255, 255)', font=font)
        y_pos += h

    img = cv2.cvtColor(np.asarray(pil_img).astype(np.uint8), cv2.COLOR_BGR2RGB)
    cv2.imwrite("done.jpg", img)
