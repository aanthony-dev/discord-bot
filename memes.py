import cv2
import urllib.request
import numpy as np

def create_image(url, top_text, bottom_text):
    #acquire the meme image
    req = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)

    #resize the meme
    resize_width = 800
    ratio = resize_width / img.shape[1]
    resized_img = cv2.resize(img, (int(img.shape[1] * ratio), int(img.shape[0] * ratio)), interpolation = cv2.INTER_AREA)
    
    print(resized_img.shape)

    #add top text
    size = cv2.getTextSize(top_text, cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, thickness=2)[0]
    print(size)

    text_width_scale = resize_width / size[0]
    print(text_width_scale)
    print(resized_img.shape[1] * text_width_scale)

    test = int((resize_width - (resized_img.shape[1] * text_width_scale)) / 2)
    print(test)

    cv2.putText(resized_img, text=top_text, org=(0, int(size[1] * text_width_scale)),
                fontFace= cv2.FONT_HERSHEY_TRIPLEX, fontScale=text_width_scale, color=(0, 0, 0),
                thickness=8)
    cv2.putText(resized_img, text=top_text, org=(0, int(size[1] * text_width_scale)),
                fontFace= cv2.FONT_HERSHEY_TRIPLEX, fontScale=text_width_scale, color=(256,256,256),
                thickness=2, lineType=cv2.LINE_AA)

    #add bottom text
    size = cv2.getTextSize(bottom_text, cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, thickness=2)[0]
    print(size)

    text_width_scale = resize_width / size[0]
    print(text_width_scale)
    print(resized_img.shape[1] * text_width_scale)

    test = int((resize_width - (resized_img.shape[1] * text_width_scale)) / 2)
    print(test)

    cv2.putText(resized_img, text=bottom_text, org=(0, resized_img.shape[0] - size[1]),
                fontFace= cv2.FONT_HERSHEY_TRIPLEX, fontScale=text_width_scale, color=(0, 0, 0),
                thickness=8, lineType=cv2.LINE_AA)
    cv2.putText(resized_img, text=bottom_text, org=(0, resized_img.shape[0] - size[1]),
                fontFace= cv2.FONT_HERSHEY_TRIPLEX, fontScale=text_width_scale, color=(256,256,256),
                thickness=2, lineType=cv2.LINE_AA)

    #save the meme
    cv2.imwrite('meme.png', resized_img)