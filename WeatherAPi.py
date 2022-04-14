import math
from datetime import date, datetime, timedelta

import requests

from api_exception import ApiException, CheckErr
from service_key import ServiceKey

service_key = ServiceKey.weather_key


def get_current_base_time(opt):
    # 오늘
    today = datetime.today()  # 현재 지역 날짜 반환
    today_date = today.strftime("%Y%m%d")  # 오늘의 날짜 (연도/월/일 반환)

    # 어제
    yesterday = date.today() - timedelta(days=1)
    yesterday_date = yesterday.strftime('%Y%m%d')

    now = datetime.now()
    hour = now.hour
    minute = now.minute

    update_time = "0030 0130 0230 0330 0430 0530 0630 0730 0830 0930 1030 1130 1230 1330 1430 1530 1630 1730 1830 " \
                  "1930 2030 2130 2230 2330".split()

    base_date = today_date
    if (hour < 1) and (minute < 30):
        today_date = yesterday_date
        base_time = update_time[23]
    elif (hour >= 1) and (minute < 30):
        base_time = update_time[hour - 1]
    else:
        base_time = update_time[hour]

    if opt == 0:
        return today, today_date, base_date, base_time
    else:
        return base_time


# 온도,습도,강수량,습도,풍속 데이터
def get_weather_info(lat, lng):
    page_no = '1'
    num_of_rows = '1000'
    data_type = 'JSON'

    nx, ny = grid(lat, lng)
    today, today_date, base_date, base_time = get_current_base_time(0)

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'

    params = {
        'serviceKey': service_key,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        'dataType': data_type,
        'base_date': today_date,
        'base_time': base_time,
        'nx': nx, 'ny': ny
    }
    try:
        response = requests.get(url, params=params)

        state_code = response.json().get('response').get('header').get('resultCode')
        CheckErr(state_code)
    except ApiException as e:
        print(e)
    datas = response.json().get('response').get('body').get('items')

    # 최종 리턴 딕션너리
    data = dict()

    base = today.strftime('%Y-%m-%d')
    data['date'] = base
    data["base_time"] = base_time
    weather_data = dict()
    compare_time = int(base_time) + 70

    if compare_time == 2400:
        compare_time = 0

    for item in datas['item']:

        category = item['category']
        predict_time = item['fcstTime']

        if int(base_date) <= int(item['fcstDate']) and compare_time == int(predict_time):

            # 온도 코드
            if category == 'T1H':
                weather_data['tmp'] = item['fcstValue']
            # 강수량 코드
            elif category == 'RN1':
                if item['fcstValue'] == "강수없음":
                    weather_data['rn1'] = "_"
                else:
                    weather_data['rn1'] = item['fcstValue']

            # 습도 코드
            elif category == 'REH':
                weather_data['reh'] = item['fcstValue']
            # 풍속 코드
            elif category == 'WSD':
                weather_data['wsd'] = item['fcstValue']
            # 하늘 상태 코드
            elif category == 'SKY':
                sky_code = item['fcstValue']
                if sky_code == '1':
                    weather_data['sky'] = '맑음'
                elif sky_code == '3':
                    weather_data['sky'] = '구름 많음'
                elif sky_code == '4':
                    weather_data['sky'] = '흐림'

            # 기상 상태
            elif category == 'PTY':
                weather_code = item['fcstValue']

                if weather_code == '1':
                    weather_state = '비'
                elif weather_code == '2':
                    weather_state = '비/눈'
                elif weather_code == '3':
                    weather_state = '눈'
                elif weather_code == '5':
                    weather_state = '빗방울'
                elif weather_code == '6':
                    weather_state = '빗방울 눈날림'
                elif weather_code == '7':
                    weather_state = '눈날림'
                else:
                    weather_state = False

                weather_data['state'] = weather_state
    data['weather'] = weather_data

    return data


# 위도 경도 , 기상청 x,y 좌표로 변경
def grid(lat, lng):
    v1, v2 = float(lat), float(lng)
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기1준점 Y좌표(GRID)

    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    rs = {}

    ra = math.tan(math.pi * 0.25 + v1 * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)

    theta = v2 * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    rs['x'] = math.floor(ra * math.sin(theta) + XO + 0.5)
    rs['y'] = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

    str_x = str(rs["x"]).split('.')[0]
    str_y = str(rs["y"]).split('.')[0]

    return str_x, str_y


if __name__ == "__main__":
    print(get_weather_info(37.3045223, 126.986331))
