import cv2 as cv
import numpy as np

from src.parser.src.ML import letters_to_str


def screenshot_as_cv2_mat(screenshot_as_png):
    nparr = np.frombuffer(screenshot_as_png, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)
    return img


def get_srt_captcha_from_screenshot(site_screenshot_as_png):
    site_screenshot_as_cv2_mat = screenshot_as_cv2_mat(site_screenshot_as_png)

    # returns
    is_damaged = False
    string_from_cap = ""

    # cut captcha image from screenshot
    captcha_size = [87, 249]
    captcha_cord = [268, 31]
    captcha = site_screenshot_as_cv2_mat[
              captcha_cord[0]:captcha_cord[0] + captcha_size[0],
              captcha_cord[1]:captcha_cord[1] + captcha_size[1]
              ]

    # extract letter's images
    letters_images = get_img_of_letters_from_captcha(captcha)
    if len(letters_images) == 5:
        string_from_cap = letters_to_str(letters_images)
    else:
        is_damaged = True

    return is_damaged, string_from_cap


def get_img_of_letters_from_captcha(img):
    out_size = 28
    letters = []
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img1 = cv.medianBlur(gray, 5)
    ret, otsu = cv.threshold(img1, 180, 255, cv.THRESH_BINARY)
    img_erode = cv.erode(otsu, np.ones((3, 3), np.uint8), iterations=1)
    # cv.imshow("img", img)
    # cv.imshow("gray", gray)
    # cv.imshow("img1", img1)
    # cv.imshow("otsu", otsu)
    # cv.imshow("img_erode", img_erode)
    # cv.waitKey(0)

    # Get contours
    contours, hierarchy = cv.findContours(img_erode, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv.boundingRect(contour)
        if hierarchy[0][idx][3] == 0:
            if h >= 20 and h >= 20:
                letter_crop = otsu[y:y + h, x:x + w]
                # Resize letter canvas to square
                size_max = max(w, h)
                letter_square = 255 * np.ones(shape=[size_max, size_max], dtype=np.uint8)
                if w > h:
                    # Enlarge image top-bottom
                    # ------
                    # ======
                    # ------
                    y_pos = size_max // 2 - h // 2
                    letter_square[y_pos:y_pos + h, 0:w] = letter_crop
                elif w < h:
                    # Enlarge image left-right
                    # --||--
                    x_pos = size_max // 2 - w // 2
                    letter_square[0:h, x_pos:x_pos + w] = letter_crop
                else:
                    letter_square = letter_crop
                letters.append((x, w, cv.resize(letter_square, (out_size, out_size), interpolation=cv.INTER_AREA)))

    letters.sort(key=lambda x: x[0], reverse=False)
    return letters
