#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt
import os


class SetApodAsWallpaper(object):
    # 오늘 날짜 계산
    today = dt.today()
    if today <= dt(today.year, today.month, today.day, 14):
        today_date = '{:0>4}{:0>2}{:0>2}'.format(today.year, today.month, today.day - 1)
    else:
        today_date = '{:0>4}{:0>2}{:0>2}'.format(today.year, today.month, today.day)

    # 바탕화면 업데이트 해야하는지 확인
    def checkUpdate(self):
        # 바탕화면으로 설정된 파일이름에서 날짜 알아내기
        current_bg = os.popen("gsettings get org.cinnamon.desktop.background picture-uri").read().strip()
        self.bg_date = current_bg.split('/')[-1].split('.')[0]
        print(self.bg_date, self.today_date)

        # 오늘 날짜와 바탕화면 날짜 비교해서 업데이트 필요 여부 리턴
        try:
            return True if int(self.today_date) > int(self.bg_date) else False
        except ValueError:
            return True

    # APOD에서 사진 URL 알아내기
    def findPictureUrl(self):
        # APOD 홈페이지 html에서 img 태그 크롤링
        apod_html = requests.get("https://apod.nasa.gov/apod/astropix.html").text
        soup_img = BeautifulSoup(apod_html, "html.parser").find_all('img')

        apod_url_address = soup_img[0]['src']  # img 태그에서 src 값 할당
        apod_url_base = 'https://apod.nasa.gov/apod/'

        self.apod_url = apod_url_base + apod_url_address  # 사진 URL

        print('find picture url')

    # 사진을 로컬저장소에 저장
    def savePicture(self):
        # 경로 및 파일 관련 변수 정의
        self.wallpaper_path = os.path.expanduser("~/wallpaper/")
        self.wallpaper_name = str(self.today_date) + ".jpg"

        # apod_byte = urlopen(self.apod_url).read()  # APOD 사진 byte 코드
        apod_byte = requests.get(self.apod_url).content  # APOD 사진 byte 코드
        # 오늘 날짜로 사진 저장
        with open('{}{}'.format(self.wallpaper_path, self.wallpaper_name), mode='wb') as img:
            img.write(apod_byte)

        print('save picture')

    # wallpaper 폴더에 파일개수가 10개 이상일 때 가장 오래된 사진 제거
    def arrangePictures(self):
        wallpapers = os.listdir(self.wallpaper_path)
        if len(wallpapers) > 10:
            rm_filepath = self.wallpaper_path + sorted(wallpapers)[0]
            os.remove(rm_filepath)

        print('arrange pictures')

    # 저장한 사진 배경화면으로 설정
    def setToWallpaper(self):
        desktop_env = os.environ.get('DESKTOP_SESSION')
        os.system("gsettings set org.{}.desktop.background picture-uri file://{}{}".format(desktop_env, self.wallpaper_path, self.wallpaper_name))
        os.system("gsettings set org.{}.desktop.background picture-options 'scaled'".format(desktop_env))

        print('set to {}{} as wallpaper'.format(self.wallpaper_path, self.wallpaper_name))


if __name__ == '__main__':
    apod = SetApodAsWallpaper()

    if apod.checkUpdate():
        apod.findPictureUrl()
        apod.savePicture()
        apod.arrangePictures()
        apod.setToWallpaper()
    else:
        pass
