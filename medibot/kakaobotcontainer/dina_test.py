#0. 모듈 import
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sys
import requests
import shutil
import xmltodict
import concurrent.futures
import random
import json
from PIL import Image
from io import BytesIO
from IPython.display import display
import folium
import webbrowser
import os
import csv    
from math import sin, cos, sqrt, atan2, pi, radians
from datetime import datetime
import pytz
import pandas as pd
import traceback
import re


application = Flask(__name__)

    
#1. favicon 오류 해결  
@application.route('/favicon.ico')
def favicon():
    return application.send_static_file('favicon.ico')
 
#2. 약 이름 검색
def seach_by_name(name_input):
    
    # E약은요 API(상세효능 정보) 호출
    emedi_api_url = 'http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList'
    emedi_params = {
        'serviceKey': 'FsAw2Tgk2O1XaJ11I2HTvPmbhF+hAaFmg61CyViMSqK6lC4V6PWH9ZUAt1Iclw17n4+cAYTwrSZ160cE4IOIcw==',
        'itemName': name_input,
        'type': 'json'
    }
    response = requests.get(emedi_api_url, params=emedi_params)
    api_data_json = response.json()
    emedi_drugs= api_data_json.get('body', {}).get('items', []) # list
    # print(emedi_drugs)
    
    # 낱알정보 CSV 파일에서 검색 - API 응답 시 데이터가 일부만 제공되어 CSV파일로 대체함
    df = pd.read_csv('./csv/Tablet_data.csv')
    # 인덱스 6,7 번 앞면 또는 뒷면 각인이 text_input 값을 포함하는 경우, result에 약 정보를 데이터프레임으로 저장 
    df = df[(df.iloc[:, 1].astype(str).str.contains(name_input, case=False, na=False))]
    grain_drugs = df.values.tolist() # 데이터 프레임을 2차원 리스트로 변환
    # print(grain_drugs)
    
    # 데이터 dictionary 만들기
    data = {
        "name_list": [],    # 이름
        "eff_list": [],     # 효능
        "image_list" : [],  # 이미지URL
        "entp_list" : [],   # 제조사
    }

    for drug in emedi_drugs:
        if drug.get('itemName'):
            data["name_list"].append(drug.get('itemName',''))
            data["eff_list"].append(drug.get('efcyQesitm','')) 
            data["image_list"].append(drug.get('itemImage',''))
            data["entp_list"].append(drug.get('entpName',''))
            # print("E약",drug.get('itemName',''))
    
    # 중복 데이터 제거
    for drug in grain_drugs:
        # 문자열에서 숫자가 있는지 확인
        index_of_digit = None
        search_name=""
        for i, char in enumerate(reversed(drug[1])):
            if char.isdigit():
                index_of_digit = len(drug[1]) - i - 1
                break
        # 숫자가 있을 경우 숫자를 포함한 그 이전까지 반환
        if index_of_digit is not None:
            search_name=drug[1][:index_of_digit+1]
            print("search_name",search_name)
        else:
        # 숫자가 없을 경우 전체 문자열 반환
            search_name=drug[1]
        # search_name가 data["name_list"]에 없을 경우에만 리스트에 추가
        key = re.compile(search_name)
        for item in data["name_list"]:
            if key.search(item) is None:
                # 품목명 1, 업소명 3, 이미지 5, 분류명 18
                data["name_list"].append(drug[1])
                data["eff_list"].append(drug[18])
                data["entp_list"].append(drug[3])
                data["image_list"].append(drug[5])
                # print("낱알",drug[1])
    
    print("약품명: ",len(data["name_list"]),"개 ", data["name_list"])
    print('seach_by_name complete')
    return data, name_input

#3. 약 식별문자 검색
def search_by_print(text_input):
    text_input=text_input.upper()
    
    # 낱알정보(식별문자 정보) CSV 파일에서 검색 - API 응답 시 데이터가 일부만 제공되어 CSV파일로 대체함   
    df = pd.read_csv('./csv/Tablet_data.csv')
    # 인덱스 6,7 번 앞면 또는 뒷면 각인이 text_input 값을 포함하는 경우, result에 약 정보를 데이터프레임으로 저장 
    df = df[(df.iloc[:, 6].astype(str).str.contains(text_input, case=False, na=False)) |
            (df.iloc[:, 7].astype(str).str.contains(text_input, case=False, na=False))]
    all_drugs = df.values.tolist() # 데이터 프레임을 2차원 리스트로 변환
    print(all_drugs)
    
    # 데이터 dictionary 만들기
    data = {
        "name_list": [],    # 이름
        "eff_list": [],     # 효능
        "image_list" : [],  # 이미지URL
        "entp_list" : [],   # 제조사
    }
    for drug in all_drugs:
        # 품목명 1, 업소명 3, 이미지 5, 분류명 18
        data["name_list"].append(drug[1])
        data["eff_list"].append(drug[18])
        data["entp_list"].append(drug[3])
        data["image_list"].append(drug[5])
        
    print("약품명: ",data["name_list"])
    print('search_by_print complete')
    return data, text_input

# ###???
# def name_input():
#     req = request.get_json()
#     name_input = req['action']['params']['medi_search']          # 사용자로 부터 약이름 가져오기
#     print('약이름 검색 part start')
#     print('user_input',name_input)
    
#     # 약검색, dictionart로 변수처리, 카카오챗봇으로 respose
#     text_input='0'
#     valid_drugs, name_input = data_process(name_input)
#     data, len_sample, len_valid = data_dict(valid_drugs)
#     red = response(data, len_sample, len_valid, name_input, text_input)

#     # detail_info()로 POST 요청 보내기
#     url = f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}"
#     response_from_post = requests.post(url, json={"name_input":name_input, "text_input": text_input})
#     print('약이름 검색 part complete')
#     return red 
# #3. 약 이미지로 검색 파트 - server2로 request 요청및 값을 json형식으로 send로 가져와서 리스트 형식으로 변환후 image_to_text.txt 에 값 저장
# @application.route("/image_input", methods=['POST'])
# def image_input():
#     req = request.get_json()    
#     user_input = req['action']['params']['image_input']       # 카카오톡으로 부터 img url 가져오기
#     print('img_input',user_input)

#     response_from_post = requests.post("https://shared-medi--hixbz.run.goorm.site/subserver", data={'data': user_input}) # post 보내고 받기
#     response_data = response_from_post.json()
#     text_input = response_data.get('data', [])  # 서버 응답에서 'data' 키를 추출
#     print('img_input',user_input)
    
#         # 리스트형식으로 변환후  저장
#         with open('image_to_text.txt', 'w') as file:
#             for item in text_input:
#                 file.write(str(item) + '\n')           
#         rep = responseimg()
#         return rep
#     else:
#         ret = responseimgerror()
#         return ret
        
#     return rep

# #4. 약 이미지 확인 파트
# @application.route("/sub_image_input", methods=['POST'])
# def sub_image_input():
#     try :
#         req = request.get_json()
#         name_input = req['action']['params']['sub_image_input'] 
#         print('약 이미지 확인 part start')
        
        
#         text_input =[]
#         with open('image_to_text.txt', 'r') as file:
#             text_input = [line.strip() for line in file]        # 저장한 값 리스트로 가져오기
#         text_input.reverse()                                    # 받아온 리스트 순서 거꾸로
#         text_input = ''.join(map(str, text_input))              # 리스트를 문자열로
#         text_input = text_input.lower()                         # 소문자로 변환

        
#         # 약검색, dictionart로 변수처리, 카카오챗봇으로 respose
#         name_input='0'
#         valid_drugs = search_medicine(text_input)        
#         data, len_sample, len_valid = data_dict(valid_drugs)            
#         rep = response(data, len_sample, len_valid, name_input, text_input )
        
        
#         # detail_info()로 POST 요청 보내기
#         url = f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}"
#         response_from_post = requests.post(url, json={"name_input":name_input, "text_input": text_input})

#         return rep
    
#     # 에러 코드 확인
#     except Exception as e:
#         traceback.print_exc()  
#         print(jsonify({'error': str(e)}), 500)  
#         ret = responseimgerror()
#         return ret 


#4. 챗봇 응답 리스트에 보여줄 샘플개수 구하기
def count(data):    
    len_all=len(data["name_list"])
    if len_all >= 3:
        len_sample = 3    
    else:
        len_sample = len(data["name_list"]) 
    print('all:',len_all)
    print('sample:',len_sample)
            
    print('data_dict complete')
    return len_all, len_sample

    
    
# #11. 카카오 챗봇 응답 처리 part(챗봇으로 보내는 json 형식으로 변환)
# def response(data, len_all, len_sample, name_input, text_input):
#     responseBody = {"version": "2.0", "template": {"outputs": []}}  # responseBody 초기화
#     items_contents=[]
    
#     for i in range(len_sample):
#         item={
#             "title": data["item_namelist"][i],
#             "description": data["efcyQesitmlist"][i],
#             "imageUrl": data["item_image_urllist"][i],
#             "link": {
#                 "web": f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}/"+str(i)
#                 }
#          }
#         items_contents.append(item)

#     if len_all >= 4:
#         responseBody = {
#             "version": "2.0",
#             "template": {
#                 "outputs": [
#                     {
#                         "listCard": {
#                             "header": {
#                                 "title": f"{len_all}개가 검색되었습니다."
#                             },
#                             "items": items_contents,
#                             "buttons": [
#                                 {
#                                     "label": "더보기",
#                                     "action": "webLink",
#                                     "webLinkUrl": f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}"
#                                 }
#                             ]
#                         }
#                     }
#                 ]
#             }
#         }
#     elif len_all >= 1:
#         responseBody = {
#             "version": "2.0",
#             "template": {
#                 "outputs": [
#                     {
#                         "listCard": {
#                             "header": {
#                                 "title": f"{len_all}개가 검색되었습니다."
#                             },
#                             "items": items_contents
#                         }
#                     }
#                 ]
#             }
#         }
#     else:
#         responseBody = {
#             "version": "2.0",
#             "template": {
#                 "outputs": [
#                     {
#                         "simpleText": {
#                             "text": "정확한 약품명을 입력해 주세요"
#                         }
#                     }
#                 ]
#             }
#         }
#     print('response complete')
#     return jsonify(responseBody)

# #12.  카카오 챗봇 응답처리 (약 이미지 검색 response) 
# def responseimg():
#     responseBody = {"version": "2.0", "template": {"outputs": []}}  # responseBody 초기화
#     items_contents=[]
#     print("responseimg start")
#     responseBody = {
#             "version": "2.0",
#             "template": {
#                 "outputs": [
#                     {
#                         "simpleText": {
#                             "text": "조회한 결과 불러오기를 눌러주세요"
#                         }
#                     }
#                 ]
#             }
#         }
#     print('response complete')
#     return jsonify(responseBody)

### Tset 구역
name_input="아스피린"
data,_=seach_by_name(name_input)
count(data)

# text_input="idg"
# data,_=search_by_print(text_input)
# count(data)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True, debug=True)