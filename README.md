# MediBot

이 프로젝트는 약품 검색과 약국 위치 조회 기능을 제공하는 웹 애플리케이션입니다. 사용자는 약품 이름, 약 이미지, 또는 약 각인을 통해 약품을 검색할 수 있으며, 입력한 주소를 기반으로 근처의 약국 위치를 지도에서 확인할 수 있습니다.

## 주요 기능

- 약품 이름 검색: 사용자가 입력한 약품 이름을 기반으로 관련 약품 정보를 검색하고 표시합니다.
- 약 이미지 검색: 사용자가 업로드한 약 이미지를 분석하여 약품 정보를 추출하고 관련 약품을 검색합니다.
- 약 각인 검색: 사용자가 입력한 약 각인을 기반으로 해당 약품을 검색하고 정보를 제공합니다.
- 약국 위치 조회: 사용자가 입력한 주소를 기반으로 근처의 약국 위치를 지도에 표시합니다.

## 사용 기술 및 라이브러리
### 백엔드
Python
Flask 웹 프레임워크
requests 라이브러리 (HTTP 요청 처리)
BeautifulSoup 라이브러리 (웹 스크래핑)
YOLO (객체 탐지 모델)
EasyOCR (광학 문자 인식 라이브러리)
OpenCV (이미지 처리 라이브러리)
Pandas (데이터 처리 및 분석 라이브러리)
NumPy (수치 연산 라이브러리)

### 프런트엔드
HTML/CSS
JavaScript
jQuery
Bootstrap

## 외부 API 및 데이터

공공데이터포털 API (약품 정보 검색)
Google Maps Geocoding API (주소 좌표 변환)
Folium 라이브러리 (지도 시각화)

## 프로젝트 구조

- server1.py: 메인 서버 파일로, Flask 애플리케이션을 구동하고 API 엔드포인트를 정의합니다.
- server2.py: 약 이미지 처리를 담당하는 서브 서버 파일입니다.
- templates/: HTML 템플릿 파일들이 위치한 디렉토리입니다.
- static/: 정적 파일(CSS, JavaScript, 이미지 등)이 위치한 디렉토리입니다.
- csv/: 약품 정보 데이터가 저장된 CSV 파일이 위치한 디렉토리입니다.
- get_img/: 사용자가 업로드한 약 이미지가 저장되는 디렉토리입니다.
- pill_Detection/, preprocessed_img/, output_results/: 약 이미지 처리 과정에서 생성되는 중간 결과물이 저장되는 디렉토리들입니다.

## 설치 및 실행 방법

- 필요한 라이브러리들을 설치합니다:
codepip install -r requirements.txt

- server1.py 파일을 실행하여 메인 서버를 구동합니다:
codepython server1.py

- server2.py 파일을 실행하여 서브 서버를 구동합니다:
codepython server2.py

- 웹 브라우저에서 http://localhost:5000으로 접속하여 애플리케이션을 사용합니다.

## 작업툴
Python 3.9.13
Visual Studio Code
GitHub
goormIDE

## 기여자
- 김진화 - 프론트 엔드
- 김민호 - 백 엔드
- 김규연 - 프론트 엔드
- 신도일 - 백 엔드
