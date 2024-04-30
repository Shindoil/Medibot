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


application = Flask(__name__)
 
    

    
#1. favicon 오류 해결  
@application.route('/favicon.ico')
def favicon():
    return application.send_static_file('favicon.ico')


            
#2. 약 이름 검색 파트
@application.route("/medi_search", methods=['POST'])
def name_input():
    req = request.get_json()
    name_input = req['action']['params']['medi_search']          # 사용자로 부터 약이름 가져오기
    print('약이름 검색 part start')
    print('user_input',name_input)
    
    # 약검색, dictionart로 변수처리, 카카오챗봇으로 respose
    text_input='0'
    valid_drugs, name_input = data_process(name_input)
    data, len_sample, len_valid = data_dict(valid_drugs)
    red = response(data, len_sample, len_valid, name_input, text_input)

    # detail_info()로 POST 요청 보내기
    url = f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}"
    response_from_post = requests.post(url, json={"name_input":name_input, "text_input": text_input})
    print('약이름 검색 part complete')
    return red    


#3. 약 이미지로 검색 파트 - server2로 request 요청및 값을 json형식으로 send로 가져와서 리스트 형식으로 변환후 image_to_text.txt 에 값 저장
@application.route("/image_input", methods=['POST'])
def image_input():
    req = request.get_json()    
    user_input = req['action']['params']['image_input']       # 카카오톡으로 부터 img url 가져오기
    if "http://" in user_input or "https://" in user_input:
        print('약 이미지 검색 part start')
        print('user_input_url',user_input)
        
        send = requests.post("https://shared-medi--hixbz.run.goorm.site/subserver", data={'data': user_input}) # post 보내고 받기
        text_input = send.json()                                                                               # json형식 받기
        text_input = json.loads(text_input)
        text_input = text_input.get('data', [])

        # 리스트형식으로 변환후  저장
        with open('image_to_text.txt', 'w') as file:
            for item in text_input:
                file.write(str(item) + '\n')           
        rep = responseimg()
        return rep
    else:
        ret = responseimgerror()
        return ret
        
        

    return rep

#4. 약 이미지 확인 파트
@application.route("/sub_image_input", methods=['POST'])
def sub_image_input():
    try :
        req = request.get_json()
        name_input = req['action']['params']['sub_image_input'] 
        print('약 이미지 확인 part start')
        
        
        text_input =[]
        with open('image_to_text.txt', 'r') as file:
            text_input = [line.strip() for line in file]        # 저장한 값 리스트로 가져오기
        text_input.reverse()                                    # 받아온 리스트 순서 거꾸로
        text_input = ''.join(map(str, text_input))              # 리스트를 문자열로
        text_input = text_input.lower()                         # 소문자로 변환

        
        # 약검색, dictionart로 변수처리, 카카오챗봇으로 respose
        name_input='0'
        valid_drugs = search_medicine(text_input)        
        data, len_sample, len_valid = data_dict(valid_drugs)            
        rep = response(data, len_sample, len_valid, name_input, text_input )
        
        
        # detail_info()로 POST 요청 보내기
        url = f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}"
        response_from_post = requests.post(url, json={"name_input":name_input, "text_input": text_input})

        return rep
    
    # 에러 코드 확인
    except Exception as e:
        traceback.print_exc()  
        print(jsonify({'error': str(e)}), 500)  
        ret = responseimgerror()
        return ret 

    
    
    
#5. 약 각인 검색 파트
@application.route("/text_input", methods=['POST'])
def text_input():
    req = request.get_json()
    text_input = req['action']['params']["text_input"]  # 사용자로부터 약 각인 가져오기
    print('약 각인 검색 part start')
    print('user_input', text_input)

    
    # 약검색, dictionart로 변수처리, 카카오챗봇으로 respose
    name_input='0'
    valid_drugs = search_medicine(text_input)  
    data, len_sample, len_valid = data_dict(valid_drugs)
    res = response(data, len_sample, len_valid, name_input, text_input)
    
    # detail_info()로 POST 요청 보내기
    url = f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}"
    response_from_post = requests.post(url, json={"name_input":name_input, "text_input": text_input})
    
    return res



#6. API 데이터 처리
def is_exact_match(item, input_value):
    # 주어진 항목에서 지정된 필드들 중 하나라도 입력값과 완전히 일치하는지 확인
    exact_fields = ["PRINT_FRONT", "PRINT_BACK"]
    for field in exact_fields:
        field_value = item.get(field, "")
        if field_value and isinstance(input_value, str) and input_value.lower() == field_value.lower():
            print('match_in_API')
            return True

    # 나머지 필드는 입력값이 포함되어 있는지 확인
    contains_fields = ["ITEM_NAME", "CLASS_NAME", "ENTP_NAME", "CHART"]
    for field in contains_fields:
        field_value = item.get(field, "")
        if field_value and isinstance(input_value, str) and input_value.lower() in field_value.lower():
            print('match_in_API')
            return True

    return False




#7. 약 각인 검색 파트 - 처리 부분
def search_medicine(input_value):
    # API URL 및 파라미터 설정
    api_url = 'http://apis.data.go.kr/1471000/MdcinGrnIdntfcInfoService01/getMdcinGrnIdntfcInfoList01'
    params = {
        'serviceKey': 'API 키 입력',
        'type': 'json'
        'numOfRows': 50
    }
    
    print('각인 검색 start')
    #API 호출 및 JSON 응답 받기
    response = requests.get(api_url, params=params)
    data = response.json()
    items = data.get('body', {}).get('items', [])
    print(data)

    # API 결과에서 완전히 일치하는 항목 추출
    exact_matches_api = [item for item in items if is_exact_match(item, input_value)]
    print(exact_matches_api)
    
    
    # CSV 파일에서 검색   
    csv_file_path = './csv/Tablet_data.csv'
    df = pd.read_csv(csv_file_path)
    # 인덱스 6,7 번 각인에서 앞면 뒷면의 값과 input_value 값의 일치여부를 가려 약품명만 result에 데이터프레임으로 저장 
    result = df[(df.iloc[:, 6].astype(str).str.contains(input_value, case=False, na=False)) |
            (df.iloc[:, 7].astype(str).str.contains(input_value, case=False, na=False))]
    exact_matches_csv = result.values.tolist() # 데이터 프레임을 리스트로 변환

    

    
    print('각인 검색 complete')
    # API 결과와 CSV 파일 결과를 결합
    #print('search_medicine: ', exact_matches_api + exact_matches_csv)
    return exact_matches_csv #exact_matches_api +










#8. 약 각인 검색 파트 - 처리(함수 모음)
 #API에서 데이터 가져오기
def get_api_data(api_url, params):
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        api_data_json = response.json()
        return api_data_json.get('body', {}).get('items', [])
    except requests.RequestException as e:
        return []

 #CSV 파일에서 검색하기
def search_in_csv(user_input, csv_file_path):
    matching_drugs = []
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if user_input.lower() in row[1].lower():
                matching_drugs.append(row)
    return matching_drugs

 #중복 제거
def remove_duplicates(api_results, csv_results):
    unique_results = []
    seen = set()

    for item in api_results + csv_results:        
        item_str = json.dumps(item, sort_keys=True)
        if item_str not in seen:
            unique_results.append(item)
            seen.add(item_str)
    
    return unique_results


#9. 약 이름 검색 파트 - 데이터 처리 
def data_process(user_input):
    print('data_process start')
    # E약은요 API 호출을 위한 매개변수
    drb_api_url = 'http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList'
    drb_params = {
        'serviceKey': 'API 키 입력',
        'pageNo': '1',
        'entpName': '',
        'itemName': user_input,
        'itemSeq': '',
        'itemImage': '',
        'efcyQesitm': '',
        'atpnWarnQesitm': '',
        'intrcQesitm': '',
        'depositMethodQesitm': '',
        'type': 'json'
    }
    # 낱알 API 호출을 위한 매개변수
    mdcin_api_url = 'http://apis.data.go.kr/1471000/MdcinGrnIdntfcInfoService01/getMdcinGrnIdntfcInfoList01'
    mdcin_params = {
        'serviceKey': 'API 키 입력',
        'item_name': user_input,
        'entp_name': '',
        'item_seq': '',
        'img_regist_ts': '',
        'pageNo': '',
        'ITEM_IMAGE': '',
        'numOfRows': '',
        'edi_code': '',
        'PRINT_FRONT':'',
        'PRINT_BACK':'',
        'type': 'json'        
    }
    all_drugs = []

    #ThreadPoolExecutor를 사용하여 병렬 처리
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(get_api_data, drb_api_url, drb_params)
        future2 = executor.submit(get_api_data, mdcin_api_url, mdcin_params)

        try:
            api_results1 = future1.result()
            api_results2 = future2.result()
            all_drugs.extend(api_results1)
            all_drugs.extend(api_results2)
        except Exception as e:
            print(f"API 호출 중 오류 발생: {e}")


    csv_file_path = './csv/Tablet_data.csv'
    csv_results = search_in_csv(user_input, csv_file_path)

    
    # 중복 제거
    key = '품목명'  # 중복 확인에 사용할 키
    unique_drugs = remove_duplicates(all_drugs, csv_results)
    unique_drugs = csv_results

    print('data_process complete')
    return unique_drugs, user_input

    # 결과 출력 등의 후속 작업 수행


#10. 약 데이터 중 필요한 데이터만 dictionary로 재배치
def data_dict(valid_drugs):
    print('data_process start')
    len_valid = len(valid_drugs)

    # 챗봇 응답 리스트에 보여줄 샘플
    if len(valid_drugs) >= 3:
        sample = valid_drugs[:3]    
    else:
        sample = valid_drugs

    len_sample = len(sample) # 샘플 개수
    print('total:',len_valid)
    print('sample:',len_sample)
    # print(valid_drugs)
    
    data = {
        "item_namelist": [],        # 이름
        "efcyQesitmlist": [],       # 효능
        "item_image_urllist" : [],  # 이미지
        "entp_namelist" : []        # 제조사
    }
    
    # 데이터 리스트 만들기
    for drug in valid_drugs:        #API 사용 시
        if isinstance(drug, dict):  # 각 요소가 딕셔너리인지 확인
            data["item_namelist"].append(drug.get('itemName','') or drug.get('ITEM_NAME',''))
            data["efcyQesitmlist"].append(drug.get('efcyQesitm','') or drug.get('CLASS_NAME',''))
            data["entp_namelist"].append(drug.get('entpName','') or drug.get('ENTP_NAME',''))
            data["item_image_urllist"].append(drug.get('itemImage','') or drug.get('ITEM_IMAGE',''))  # 이미지 URL 가져오기
            # print(f"약물 이름: {drug.get('itemName','')}") #제조사: {drug.get('entpName','')}, 효능: {drug.get('efcyQesitm','')}")
        else:   # csv 사용 시
                # 품목명 1, 업소명 3, 이미지 5, 분류명 18
            data["item_namelist"].append(drug[1])
            data["efcyQesitmlist"].append(drug[18])
            data["entp_namelist"].append(drug[3])
            data["item_image_urllist"].append(drug[5])
            #print('csv:', drug[1], drug[18], drug[3], drug[5])
            
            
    print('data_dict complete')
    return data, len_sample, len_valid



#11. 카카오 챗봇 응답 처리 part(챗봇으로 보내는 json 형식으로 변환)
def response(data, len_sample, len_valid, name_input, text_input):
    responseBody = {"version": "2.0", "template": {"outputs": []}}  # responseBody 초기화
    items_contents=[]
    print("response start")
    
    for i in range(len_sample):
        item={
            "title": data["item_namelist"][i],
            "description": data["efcyQesitmlist"][i],
            "imageUrl": data["item_image_urllist"][i],
            "link": {
                "web": f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}/"+str(i)
                }
         }
        items_contents.append(item)

    if len_valid >= 4:
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": f"{len_valid}개가 검색되었습니다."
                            },
                            "items": items_contents,
                            "buttons": [
                                {
                                    "label": "더보기",
                                    "action": "webLink",
                                    "webLinkUrl": f"https://kakaobotcontainer-rbcrp.run.goorm.site/{name_input}/{text_input}"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    elif len_valid >= 1:
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": f"{len_valid}개가 검색되었습니다."
                            },
                            "items": items_contents
                        }
                    }
                ]
            }
        }
    else:
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "정확한 약품명을 입력해 주세요"
                        }
                    }
                ]
            }
        }
    print('response complete')
    return jsonify(responseBody)

#12.  카카오 챗봇 응답처리 (약 이미지 검색 response) 
def responseimg():
    responseBody = {"version": "2.0", "template": {"outputs": []}}  # responseBody 초기화
    items_contents=[]
    print("responseimg start")
    responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "조회한 결과 불러오기를 눌러주세요"
                        }
                    }
                ]
            }
        }
    print('response complete')
    return jsonify(responseBody)


#13.  카카오 챗봇 응답처리 (약 이미지 검색 error response) 
def responseimgerror():
    responseBody = {"version": "2.0", "template": {"outputs": []}}  # responseBody 초기화
    items_contents=[]
    print("responseimgerror start")
    responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "조회를 하지 않으셨습니다."
                        }
                    }
                ]
            }
        }
    print('response complete')
    return jsonify(responseBody)





#14. 상세 정보 페이지 연결
@application.route("/<name_input>/<text_input>/<int:index>", methods=['GET', 'POST'])
def detail_info(name_input, text_input, index):
    
    print('detail_info start')
        
    user_input=''
    valid_drugs=''
    
    if text_input=='0':
        valid_drugs, _ = data_process(name_input)
        user_input=name_input
    else:
        valid_drugs = search_medicine(text_input)
        user_input=text_input
    data, _, _ = data_dict(valid_drugs)
    
    name_list = data["item_namelist"]
    img_list = data["item_image_urllist"]
    eff_list=data["efcyQesitmlist"]
    com_list=data["entp_namelist"]
    
    

    if request.method == 'POST' or request.method == 'GET':
        return render_template("index.html", name=name_list[index], img=img_list[index], eff=eff_list[index], com=com_list[index])
        

#15. 전체 list 페이지 연결
@application.route("/<name_input>/<text_input>",methods=['GET', 'POST'])
def all_list(name_input, text_input):
    
    print('전체 list start')
    
    user_input=''
    valid_drugs=''
    if text_input=='0':
        user_input=name_input
        valid_drugs, name_input = data_process(user_input)
        
    else:
        valid_drugs = search_medicine(text_input)
        user_input=text_input
    print('각인 전체 리스트 end')
    
    data, _, _ = data_dict(valid_drugs)
    name_list = data["item_namelist"]
    img_list = data["item_image_urllist"]

    print('전제 약품이름 리스트 end ')
    
    
    while len(name_list) < 10:
        name_list.append('')
        img_list.append('https://proxy.goorm.io/service/659505cfe93b401d1e6806e9_d3af2lf7OyaWTWScDvV.run.goorm.io/9080/file/load/none_img.png?path=d29ya3NwYWNlJTJGa2FrYW9ib3Rjb250YWluZXIlMkZ0ZW1wbGF0ZXMlMkZub25lX2ltZy5wbmc=&docker_id=d3af2lf7OyaWTWScDvV&secure_session_id=-smQvN_UPV9JRmlCSgMIDcWTWoyqOLK8')
    
    if request.method == 'POST' or request.method == 'GET':
        return render_template("index_all.html", name_input=name_input, text_input=text_input,
                                img0=img_list[0], img1=img_list[1], img2=img_list[2], img3=img_list[3], img4=img_list[4], img5=img_list[5], img6=img_list[6], img7=img_list[7], img8=img_list[8], img9=img_list[9],
                                name0=name_list[0], name1=name_list[1], name2=name_list[2], name3=name_list[3], name4=name_list[4], name5=name_list[5], name6=name_list[6], name7=name_list[7], name8=name_list[8], name9=name_list[9])

    

    
#16. 약국 조회 파트  
@application.route("/pham_loc", methods=['POST'])
def pham_loc():
    req = request.get_json()
    
    user_input = req['action']['params']['pham_loc'] # 사용자 주소 가져오기
    print('약국 조회 파트 start')
    print('user_input',user_input)
    res=get_geo_api(user_input)

    return res
    
    
    
#17. 약국 조회 처리 geo_code(사용자 입력주소 좌표변환), forlium(지도 시각화) 
def get_geo_api(user_input):
    print('약국 조회 처리 part start')
    api_key = "AIzaSyAkVCM0BzXTQIHFZ-FnI_lWgIrUte_I_UU"                 # 구글 maps api_key
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": user_input,
        "key": api_key,
    }

    response = requests.get(base_url, params=params)                    # 사용자 주소 가져오기
    result = response.json()    
    user_coord = None  # 좌표 변수 초기화

    if response.status_code == 200 and result["status"] == "OK":
        location = result["results"][0]["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
        user_coord = [latitude, longitude]
        
        #유저 위치저장및 확인
        file_path = 'testdata/user_location.txt'
        with open(file_path, 'w') as file:
            for coord in user_coord:
                file.write(f"{coord}\n")

    else:
        print(f"Geocoding failed. Status Code: {response.status_code}, Result: {result}")
        user_coord = None
    
    # 지도 마커 추가
    def add_marker(map_object, location, popup_text, marker_color='red'):                   
            folium.Marker(
                location=location,
                popup=folium.Popup(popup_text, parse_html=True),
                icon=folium.Icon(color=marker_color)
            ).add_to(map_object)

    
    # 지도 초기화,변수선언,리스트 선언
    map_center = []
    coordinates_list = []
    save_list = []
    csv_file_path = 'testdata/pharmacy.csv'
    desired_column_indices = [22, 23]

    dis_list = []

    # 내위치 기준 맵중앙시작 + 내위치 마커추가
    with open('testdata/user_location.txt', 'r') as file:
            lines = file.readlines()

            for line in lines:
            # 좌표값을 실수형으로 변환하여 리스트에 추가
                map_center.append(float(line.strip()))
            # 지도 중심 설정
            my_map = folium.Map(location=map_center, zoom_start=15)
            # 내위치 마커추가
            icon_class = "fas fa-location-crosshairs"
            folium.Marker(location=map_center, icon=folium.Icon(color='blue', icon=icon_class, prefix='fa'), popup='내위치', icon_size=(30, 30)).add_to(my_map)

    # 약국 정보 csv 가져오기 + 시간 반영해서 약국 위치 마커 추가            
    with open(csv_file_path, 'r', encoding='euc-kr') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            now = datetime.now()
            print(now)                   # 현재 시간 확인
            ccurrent_day = now.day
            current_year = now.year
            current_month = now.month
            current_hour = now.hour+9
            if current_hour > 24 :
                current_hour = current_hour - 24



            current_minute = now.minute
            time_combined = f"{current_hour:02d}{current_minute:02d}"
            
            

            date_string = str(now)
            date_format="%Y-%m-%d"
            date_str = (str(current_year)+'-'+str(current_month)+'-'+str(ccurrent_day))

            date_object = datetime.strptime(date_str, date_format)
            day_of_week = date_object.weekday()
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

            # 지구 거리반영해서 좌표차이로 실제거리 계산
            for row in csv_reader:    
                coordinates = [float(row[index]) for index in desired_column_indices] + [row[2]] + [row[3]]+ [row[4]]+ [row[5]]+ [row[6]]+ [row[7]]+ [row[8]]+ [row[9]]+ [row[10]]+ [row[12]]+ [row[13]]+ [row[14]]+ [row[15]]+ [row[16]]+ [row[17]]+ [row[18]]

                coordinates_list = []
                coordinates_list.append(coordinates)


                for lat1, lon1, name ,phone, mon_c,tue_c,wed_c,thu_c,fri_c,sat_c,sun_c,mon_o,tue_o,wed_o,thu_o,fri_o,sat_o,sun_o in coordinates_list:
                    lat2, lon2 = map_center

                    lata = lat1
                    lona = lon1
                    lat1 = lat1 *pi/180

                    lat2 = lat2 *pi/180
                    lon1 = lon1 *pi/180

                    lon2 = lon2 *pi/180

                    R = 6371  # radius of Earth in kilometers


                    dlat = (lat2 - lon1)
                    dlon = (lon2 - lat1)

                    if dlat < 0:
                        dlat = -dlat
                    if dlon <0:
                        dlon = -dlon




                    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                    if a <0:
                        a = -a
                    c = 2 * atan2(sqrt(a), sqrt(1 - a))


                    distance = R * c 
                    if distance < 1.5 :                    
                        dis_list.append((distance, [lona, lata],name,phone, mon_c,tue_c,wed_c,thu_c,fri_c,sat_c,sun_c,mon_o,tue_o,wed_o,thu_o,fri_o,sat_o,sun_o))
            
            # 가까운 순서로 정렬
            dis_list = sorted(dis_list, key=lambda x: x[0])[:20]





            
            # 추가 위치 좌표 추가(요일대로 현재시간과 약국운영시간 비교해서 마크색 반영 빨간색-open 검은색-cloes)
            # 약국위치 전화번호 반환 
            for (dis, coo,name,phone, mon_c,tue_c,wed_c,thu_c,fri_c,sat_c,sun_c,mon_o,tue_o,wed_o,thu_o,fri_o,sat_o,sun_o) in dis_list:
                icon_class = "fas fa-mortar-pestle"
                
                if days[day_of_week] == 'mon':
                    if time_combined > mon_o and time_combined < mon_c:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='red', icon=icon_class, prefix='fa')).add_to(my_map)

                    else:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='black', icon=icon_class, prefix='fa')).add_to(my_map)


                elif days[day_of_week] == 'tue':
                    if time_combined > tue_o and time_combined < tue_c:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='red', icon=icon_class, prefix='fa')).add_to(my_map)

                    else:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='black', icon=icon_class, prefix='fa')).add_to(my_map)


                elif days[day_of_week] == 'wed':
                    if time_combined  > wed_o and time_combined < wed_c:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='red', icon=icon_class, prefix='fa')).add_to(my_map)

                    else:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='black', icon=icon_class, prefix='fa')).add_to(my_map)


                elif days[day_of_week] == 'thu':
                    if time_combined  > thu_o and time_combined < thu_c:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='red', icon=icon_class, prefix='fa')).add_to(my_map)
                        
                    else:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='black', icon=icon_class, prefix='fa')).add_to(my_map)                        


                elif days[day_of_week] == 'fri':
                    if time_combined  > fri_o and time_combined < fri_c:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='red', icon=icon_class, prefix='fa')).add_to(my_map)

                    else:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='black', icon=icon_class, prefix='fa')).add_to(my_map)


                elif days[day_of_week] == 'sat':
                    if time_combined > sat_o and time_combined < sat_c:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='red', icon=icon_class, prefix='fa')).add_to(my_map)

                    else:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='black', icon=icon_class, prefix='fa')).add_to(my_map)


                elif days[day_of_week] == 'sun':
                    if time_combined  > sun_o and time_combined < sun_c:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='red', icon=icon_class, prefix='fa')).add_to(my_map)

                    else:
                        folium.Marker(location=[coo[0], coo[1]], popup=f'{name} - 전화번호: {phone} ', icon=folium.Icon(color='black', icon=icon_class, prefix='fa')).add_to(my_map)


                else :
                    pass

            print('약국 조회 처리 part complete')
            html_file_path = 'map_with_markers.html'
            my_map.save(html_file_path)
            
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": f"{user_input}의 약국 정보입니다."
                            }
                        },
                        {
                            "basicCard": {
                                "title": "위치조회",
                                "thumbnail": {
                                    "imageUrl": "https://proxy.goorm.io/service/659505cfe93b401d1e6806e9_d3af2lf7OyaWTWScDvV.run.goorm.io/9080/file/load/mapicon.jpg?path=d29ya3NwYWNlJTJGa2FrYW9ib3Rjb250YWluZXIlMkZ0ZW1wbGF0ZXMlMkZtYXBpY29uLmpwZw==&docker_id=d3af2lf7OyaWTWScDvV&secure_session_id=DfnInBUHpLl72Pr8--AbJZckvH_qT8ns"
                                },
                                "buttons": [
                                    {
                                        "action": "webLink",
                                        "label": "지도보기",
                                        "webLinkUrl": "https://kakaobotcontainer-rbcrp.run.goorm.site/41"
                                    }
                                ]
                            }    
                        }
                    ]
                }
            }

            return jsonify(responseBody)


#18. 지도 url 출력 
@application.route('/41')
def index():
    original_path = '/workspace/kakaobotcontainer/map_with_markers.html'
    new_path = '/workspace/kakaobotcontainer/templates/map_with_markers.html'
    
    if os.path.exists(original_path):
        shutil.move(original_path, new_path)
        return render_template('map_with_markers.html')
    else:
        return render_template('map_with_markers.html')


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
    