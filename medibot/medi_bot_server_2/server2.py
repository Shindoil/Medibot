import ultralytics
from ultralytics import YOLO
import torch
from PIL import Image
import cv2
import multiprocessing
import easyocr
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
from flask import Flask, request , jsonify
import requests
from io import BytesIO
from PIL import Image
import json
import shutil

application = Flask(__name__)

def remove_directories(directories):
    for dir in directories:
        if os.path.exists(dir):
            shutil.rmtree(dir)

@application.route('/subserver', methods=['POST','GET'])
def subserver():
    # 디렉토리 삭제 로직
    directories_to_remove = ['pill_Detection', 'preprocessed_img', 'output_results']
    remove_directories(directories_to_remove)

    # 요청으로부터 이미지 URL 가져오기
    url = request.form['data']
    response = requests.get(url)
    response.raise_for_status()

    # 이미지 처리 로직
    image = Image.open(BytesIO(response.content))
    image.save("./get_img/1.jpg")

    reader = easyocr.Reader(['en','ko'])
    source = './get_img'
    go =[]

    # 이미지를 입력받아 택스트부분만 이미지로 추출
    def get_img(source):
        load_model = YOLO('./model/best.pt')
        result = load_model.predict(source, project='pill_Detection', save_crop=True, conf=0.5)

    folder_paths = ['./pill_Detection/predict/crops/f_text', './pill_Detection/predict/crops/b_text']
    processed_img_dir = './preprocessed_img/'

    def preprocess_img(folder_paths, processed_img_dir):
        if not os.path.exists(processed_img_dir):
            os.makedirs(processed_img_dir)
        for folder_path in folder_paths:
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path) and file_path.lower().endswith(('.jpg','png')):
                        img = cv2.imread(file_path)
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        denoised_img = cv2.medianBlur(gray, 7)
                        alpha = -2.4 
                        contrast_img = np.clip((1+alpha) * denoised_img - 128 * alpha, 0, 255).astype(np.uint8)
                        inverted_image = cv2.bitwise_not(contrast_img)
                        threshold_img = cv2.adaptiveThreshold(inverted_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                              cv2.THRESH_BINARY, 73, 3.5)
                        processed_file_path = os.path.join(processed_img_dir, filename)
                        cv2.imwrite(processed_file_path, threshold_img)

    output_text_dir = './output_results/'
    
    # 저장된 이미지에서 텍스트를 읽어내어 반환
    def read_img_to_text(img_input_directory, output_text_directory):
        if not os.path.exists(output_text_directory):
            os.makedirs(output_text_directory)
        for filename in os.listdir(img_input_directory):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                file_path = os.path.join(img_input_directory, filename)
                result = reader.readtext(file_path)
                output_file_path = os.path.join(output_text_directory, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    for detection in result:
                        file.write(detection[1] + "\n")
                print(f"Results for {filename}:")
                for detection in result:
                    print(detection[1])
                    go.append(detection[1])
                print("\n")

    get_img(source)
    preprocess_img(folder_paths, processed_img_dir)
    read_img_to_text(processed_img_dir, output_text_dir)
    
    
    json_data = json.dumps({'data': go})
    
    
    return jsonify(json_data) 

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
