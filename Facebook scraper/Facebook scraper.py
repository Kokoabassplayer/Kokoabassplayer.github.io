#import library (ถ้าทำครั้งแรกต้อง install ก่อน)
import pandas as pd

#import Facebook_scraper class from facebook_page_scraper
from facebook_page_scraper import Facebook_scraper

page_name = "ondemandacademy" #เลือกเพจที่จะ scrape โดยดึงจาก / สุดท้าย เช่น https://www.facebook.com/ondemandacademy
posts_count = 100 #เลือกจำนวนโพสที่จะ scraoe
browser = "firefox"
proxy = "IP:PORT" 
timeout = 600 
headless = True
post_scrape = Facebook_scraper(page_name, posts_count, browser, proxy=proxy, timeout=timeout, headless=headless)

file_name = "ondeamnd_scrape" #ตั้งชื่อไฟล์
directory = "D:\PYTHON\Facebook scraper" #path ที่จะให้เก็บไฟล์ กด copy path จาก folder ข้างๆได้
csv_data = post_scrape.scrap_to_csv(file_name, directory)