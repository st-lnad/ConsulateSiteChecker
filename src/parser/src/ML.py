from json import load

import numpy as np
from tensorflow.keras.models import load_model

config_file = open('src/parser/cfg/Config.json', 'r')
config = load(config_file)
config_file.close()

emnist_labels = config["ML"]["emnist_labels"]
model_path = config["ML"]["model_path"]


def letters_to_str(letters):
    model = load_model(model_path)
    s_out = ""
    for i in range(len(letters)):
        s_out += emnist_predict_img(model, letters[i][2])
    s_out = s_out.upper()
    # print(s_out, len(s_out))
    return s_out


def emnist_predict_img(model, img):
    img_arr = np.expand_dims(img, axis=0)
    img_arr = 1 - img_arr / 255.0
    img_arr[0] = np.rot90(img_arr[0], 3)
    img_arr[0] = np.fliplr(img_arr[0])
    img_arr = img_arr.reshape((1, 28, 28, 1))

    result = model.predict_classes([img_arr])
    return chr(emnist_labels[result[0]])
