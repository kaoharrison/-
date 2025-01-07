from dash import Dash, html, dcc, Input, Output, dash_table, callback, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import io
import plotly.express as px
from src.const import get_constants
import random 
import plotly.graph_objects as go
import plotly.colors as pc
import geopandas as gpd
import dash_leaflet as dl
import json
from dash.dependencies import Input, Output, State

# 導入其他模組中的函數
from src.generate_visualization import generate_bar, generate_pie, generate_map, generate_box
from src.data_clean import travel_data_clean, countryinfo_data_clean, data_merge

# 加載資料
precipitation_df = pd.read_csv('data/商管程式設計_資料集_降雨量_v1.csv')
temperature_df = pd.read_csv('data/商管程式設計_資料集_氣溫_v1.csv')
lightduration_df = pd.read_csv('data/Average Duration of Daylight.csv')
suntime_df = pd.read_csv('data/Sunrise Sunset Time.csv')

# Convert necessary columns to numeric if they are not already
precipitation_df['Precipitation'] = pd.to_numeric(precipitation_df['Precipitation'], errors='coerce')
temperature_df['Temperature'] = pd.to_numeric(temperature_df['Temperature'], errors='coerce')
lightduration_df['Hours'] = pd.to_numeric(lightduration_df['Hours'], errors='coerce')
suntime_df['Time'] = pd.to_numeric(suntime_df['Time'], errors='coerce')

# Drop NaN values from temperature_df to ensure clean data for plotting
temperature_df = temperature_df.dropna(subset=['Month', 'Temperature'])
suntime_df = suntime_df.dropna(subset=['Month', 'Time']) 

# Ensure 'Month' column is treated as categorical and ordered for proper plotting
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
temperature_df['Month'] = pd.Categorical(temperature_df['Month'], categories=month_order, ordered=True)
suntime_df['Month'] = pd.Categorical(suntime_df['Month'], categories=month_order, ordered=True)

# Get category list
category_list = list(precipitation_df['Category'].unique())
category_list_lightduration = list(lightduration_df['Category'].unique())


###千瑜景點部分
# 讀取文字雲資料
data = pd.read_csv('data/景點資料集/台北市遊憩地點流量統計(文字雲Oct).csv')  # 替換為正確的檔案路徑
wordcloud_data = dict(zip(data['Location'], data['Amount']))

#定義漸層色
def random_color(*args, **kwargs):
    colors = ["#314572", "#657495", "#98a2b8", "#ccd0dc"]  # 漸層顏色
    return random.choice(colors)

# 生成文字雲函式
def generate_wordcloud(data):
    # 將 width / height 設得更大，讓 WordCloud 產生更多像素
    wc = WordCloud(
        width=2400,
        height=600,
        background_color='white',
        color_func=random_color,  # 使用漸層顏色
        prefer_horizontal=1.0
    )
    wc.generate_from_frequencies(data)

    # 利用 plt.figure(...) 設置更大的 figure size，以及較高的 dpi
    img = io.BytesIO()
    plt.figure(figsize=(12, 6), dpi=150)  # figsize=(寬, 高), dpi=150~300 均可嘗試
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    
    # 在 savefig 時也可以再指定 dpi
    plt.savefig(img, format='png', bbox_inches='tight', dpi=150)
    plt.close()  # 避免重複顯示或佔用記憶體

    img.seek(0)
    encoded_image = base64.b64encode(img.getvalue()).decode()
    return f"data:image/png;base64,{encoded_image}"
   

# 生成文字雲圖片
wordcloud_image = generate_wordcloud(wordcloud_data)

# 地區對應圖片檔案名稱與說明
locations = {
    "Shilin": [
        {"src": "士林1.jpg", "description": "Chiang Kai-shek Shilin Residence Park", "link": "https://www.google.com/maps/place/%E5%A3%AB%E6%9E%97%E5%AE%98%E9%82%B8%E5%85%AC%E5%9C%92/@25.0913793,121.5291642,17z/data=!3m1!4b1!4m6!3m5!1s0x3442af53ab8db519:0x5e84b4b021177ad4!8m2!3d25.0913793!4d121.5291642!16s%2Fg%2F11q3mmvcdc?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "士林2.jpg", "description": "Garden Mall", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJAfF2r9CuQjQR_oP78z_fWqA"},
        {"src": "士林3.jpg", "description": "Qingtiangang Grassland", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJNehVjGSyQjQRiHAgVTN2Gdk"},
        {"src": "士林4.jpg", "description": "Nightscape-viewing from Yangmingshan", "link": "https://www.google.com/maps/place/%E6%96%87%E5%8C%96%E5%A4%A7%E5%AD%B8%E5%BE%8C%E5%B1%B1/@25.1340326,121.5394789,17z/data=!3m1!4b1!4m6!3m5!1s0x3442addf4a4b4abb:0xafe5628db340799b!8m2!3d25.1340326!4d121.5394789!16s%2Fg%2F11b6pwcy1s?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "士林5.jpg", "description": "Shezi Daotou Park", "link": "https://www.google.com/maps/place/%E7%A4%BE%E5%AD%90%E5%B3%B6+%E5%B3%B6%E9%A0%AD%E5%85%AC%E5%9C%92/@25.1098485,121.4660588,17z/data=!3m1!4b1!4m6!3m5!1s0x3442af40fb4aaf57:0x7af220d15d703302!8m2!3d25.1098485!4d121.4660588!16s%2Fg%2F11b6_t8tn7?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "士林6.jpg", "description": "National Palace Museum", "link": "https://www.google.com/maps/place/%E5%9C%8B%E7%AB%8B%E6%95%85%E5%AE%AE%E5%8D%9A%E7%89%A9%E9%99%A2/@25.1023554,121.5484925,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ac3acd404a7d:0x5d6d7018397a09c1!8m2!3d25.1023554!4d121.5484925!16zL20vMGhod2w?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"}
    ],
    "Datong": [
        {"src": "大同1.jpg", "description": "Ningxia Road Night Market", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJxUXPVmupQjQRtBB6oj-S5qI"},
        {"src": "大同2.jpg", "description": "Xiahai City God Temple", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJeXELiROpQjQR1REJMdOO8Xo"},
        {"src": "大同3.jpg", "description": "Taipei Confucius Temple", "link": "https://www.google.com/maps/place/%E6%B0%B8%E6%A8%82%E5%B8%82%E5%A0%B4/@25.0548835,121.5104598,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a91395a75315:0xe57e9a689748e5fe!8m2!3d25.0548835!4d121.5104598!16s%2Fg%2F11c0p_0546?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "大同4.jpg", "description": "Taipei Confucius Temple", "link": "https://www.google.com/maps/place/%E5%8F%B0%E5%8C%97%E9%9C%9E%E6%B5%B7%E5%9F%8E%E9%9A%8D%E5%BB%9F/@25.0555941,121.5102169,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a9147253c4e7:0x696d3ec54fe173d2!8m2!3d25.0555941!4d121.5102169!16s%2Fg%2F11x7vx8qn?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "大同5.jpg", "description": "Taipei Confucius Temple", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJc-TxSWypQjQR-8Eh7elK97Q"},
        {"src": "大同6.jpg", "description": "Taipei Confucius Temple", "link": "https://www.google.com/maps/place/%E6%9D%8E%E8%87%A8%E7%A7%8B%E6%95%85%E5%B1%85/@25.055159,121.5087384,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a913fee79775:0xb02a77fa292d8f5d!8m2!3d25.055159!4d121.5087384!16s%2Fg%2F11b7lnk77q?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"}
    ],
    "Da'an": [
        {"src": "大安1.jpg",  "link": "https://www.google.com/maps/place/%E8%87%A8%E6%B1%9F%E8%A1%97%E8%A7%80%E5%85%89%E5%A4%9C%E5%B8%82/@25.0301412,121.5542672,17z/data=!3m1!4b1!4m6!3m5!1s0x3442abcb3e5a8b07:0xba5d7dc78fba5d2e!8m2!3d25.0301412!4d121.5542672!16s%2Fm%2F0nbdb6l?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D","description": "Linjiang Street Night Market"},
        {"src": "大安2.jpg", "description": "Jianguo Holiday Flower Market", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJyzI27tWrQjQR5LW9lltBmHA"},
        {"src": "大安3.jpg", "description": "Fuyang Eco Park", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJfQNTLDiqQjQRfVU8bVpiGS0"},
        {"src": "大安4.jpg", "description": "Liang Shi-Qiu's Residence", "link": "https://www.google.com/maps/place/%E6%A2%81%E5%AF%A6%E7%A7%8B%E6%95%85%E5%B1%85(%E9%96%8B%E9%A4%A8%E6%99%82%E9%96%93%E8%AB%8B%E8%A6%8B%E6%9C%80%E6%96%B0%E5%8B%95%E6%85%8B)/@25.0236852,121.5278549,17z/data=!4m6!3m5!1s0x3442a98f85180a6d:0x50079ce7e11c6dc6!8m2!3d25.0238237!4d121.5278787!16s%2Fg%2F1pzsgqzx0?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "大安5.jpg", "description": "Huanmin Village on Chanchushan", "link": "https://www.google.com/maps/place/%E8%9F%BE%E8%9C%8D%E5%B1%B1%E8%81%9A%E8%90%BD%E6%96%87%E5%8C%96%E4%B8%AD%E5%BF%83+%E7%85%A5%E6%B0%91%E6%96%B0%E6%9D%91/@25.0094299,121.539334,17z/data=!4m6!3m5!1s0x3442aa1fa3149677:0x8542b77d5cb24c7f!8m2!3d25.0094299!4d121.539334!16s%2Fg%2F11c5_h32gq?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "大安6.jpg", "description": "Wisteria Tea House", "link": "https://www.google.com/maps/place/%E7%B4%AB%E8%97%A4%E5%BB%AC/@25.0245532,121.5319148,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a987b3066f4d:0x493bbf0b143e0d44!8m2!3d25.0245484!4d121.5344844!16s%2Fm%2F0dljn96?entry=ttu&g_ep=EgoyMDI0MTExMS4wIKXMDSoASAFQAw%3D%3D"},
    ],
    "Zhongshan": [
        {"src": "中山1.jpg", "description": "Taipei Fine Arts Museum", "link": "https://www.google.com/maps/place/%E8%87%BA%E5%8C%97%E5%B8%82%E7%AB%8B%E7%BE%8E%E8%A1%93%E9%A4%A8/@25.0724118,121.5248102,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a951fdd9f7f9:0x7a40c3880c03a171!8m2!3d25.0724118!4d121.5248102!16s%2Fm%2F02pv6ft?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "中山2.jpg", "description": "Fish Art Center", "link": "https://www.google.com/maps/place/%E7%A7%8B%E5%88%80%E9%AD%9A%E8%97%9D%E8%A1%93%E4%B8%AD%E5%BF%83/@25.0783541,121.5641435,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ac7214cb28ab:0x1f231ffa8c3deab5!8m2!3d25.0783541!4d121.5641435!16s%2Fg%2F1pztxppvz?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "中山3.jpg", "description": "MAISON ACME", "link": "https://www.google.com/maps/place/MAISON+ACME%EF%BD%9C%E5%9C%93%E5%B1%B1%E5%88%A5%E9%82%B8/@25.0731119,121.5220184,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a951fdd9f7f9:0x6f859afa18f5c02b!8m2!3d25.0731071!4d121.5245933!16s%2Fm%2F0ds4nt6?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "中山4.jpg", "description": "Fortunetelling Street", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJKwnnCFmpQjQROYoc6QFyOSg"},
        {"src": "中山5.jpg", "description": "Liaoning Street Night Market", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJtT7-mt6rQjQRGmGNfP5nQKA"},
        {"src": "中山6.jpg", "description": "SPOT-Taipei Film House", "link": "https://www.google.com/maps/place/%E5%85%89%E9%BB%9E%E5%8F%B0%E5%8C%97(%E5%8F%B0%E5%8C%97%E4%B9%8B%E5%AE%B6)/@25.053279,121.5221609,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a9692373a641:0xbd0e5da84113d393!8m2!3d25.053279!4d121.5221609!16s%2Fm%2F09gnmz7?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"}

    ],
    "Zhongzheng": [
        {"src": "中正1.jpg", "description": "Chiang Kai-shek Memorial Hall", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJTamiuZ2pQjQRsmnfkkID6UM"},
        {"src": "中正2.jpg", "description": "Huashan 1914 Creative Park", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJbSTgI2WpQjQRcVwWB2cnyfE"},
        {"src": "中正3.jpg", "description": "South Airport Night Market", "link": "https://www.google.com/maps/place/%E5%8D%97%E6%A9%9F%E5%A0%B4%E5%A4%9C%E5%B8%82/@25.0291811,121.5059244,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a9b1b0aaddbf:0x2da96f69cab8853d!8m2!3d25.0291811!4d121.5059244!16s%2Fg%2F119pgqm35?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "中正4.jpg", "description": "Treasure Hill", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJHRaGKW6pQjQRrTQrQHuZkhI"},
        {"src": "中正5.jpg", "description": "Taipei Botanical Garden", "link": "https://www.google.com/maps/place/%E8%87%BA%E5%8C%97%E6%A4%8D%E7%89%A9%E5%9C%92/@25.0318511,121.5094593,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a94f3712507b:0x890e4a55e21e821!8m2!3d25.0318511!4d121.5094593!16s%2Fm%2F0cm8h1g?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "中正6.jpg", "description": "National Taiwan Museum (Taiwan Land Bank Exhibition Hall)", "link": "https://www.google.com/maps/place/%E5%9C%8B%E7%AB%8B%E8%87%BA%E7%81%A3%E5%8D%9A%E7%89%A9%E9%A4%A8+%E5%8F%A4%E7%94%9F%E7%89%A9%E9%A4%A8/@25.0436478,121.5117892,17z/data=!3m2!4b1!5s0x3442a973550e374b:0xe38059227fbda9f2!4m6!3m5!1s0x3442a9735535556b:0x4b539419d9d989e8!8m2!3d25.043643!4d121.5143695!16s%2Fg%2F155qy3__?entry=ttu&g_ep=EgoyMDI0MTExMi4wIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"}

    ],
    "Beitou": [
        {"src": "北投1.jpg", "description": "Yangmingshuwu", "link": "https://www.google.com/maps/place/%E9%99%BD%E6%98%8E%E6%9B%B8%E5%B1%8B/@25.1616276,121.5389376,17z/data=!3m1!4b1!4m6!3m5!1s0x3442b2010fe5143d:0xd9e248f5e3604927!8m2!3d25.1616276!4d121.5389376!16s%2Fm%2F0dlmmyn?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "北投2.jpg", "description": "Bamboo Lake Alocasia Season", "link": "https://www.google.com/maps/place/%E7%AB%B9%E5%AD%90%E6%B9%96%E6%B5%B7%E8%8A%8B%E5%9C%92/@25.1770955,121.5328884,16z/data=!4m10!1m2!2m1!1z56u55a2Q5rmW5rW36IqL5a2j!3m6!1s0x3442b21fb248ff0b:0x6da4ad01a757e0af!8m2!3d25.1755535!4d121.5353966!15sChLnq7nlrZDmuZbmtbfoiovlraNaGCIW56u55a2QIOa5liDmtbcg6IqLIOWto5IBEnRvdXJpc3RfYXR0cmFjdGlvbpoBJENoZERTVWhOTUc5blMwVkpRMEZuU1VOTGVIWmlTRGhuUlJBQuABAPoBBAgAECI!16s%2Fg%2F1tctc955?authuser=0&entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "北投3.jpg", "description": "Beitou Library", "link": "https://www.google.com/maps/place/%E8%87%BA%E5%8C%97%E5%B8%82%E7%AB%8B%E5%9C%96%E6%9B%B8%E9%A4%A8+%E5%8C%97%E6%8A%95%E5%88%86%E9%A4%A8/@25.1364397,121.5062909,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ae44dacc500b:0xc8f479e8fd6e0a1d!8m2!3d25.1364397!4d121.5062909!16s%2Fm%2F0406xs9?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "北投4.jpg", "description": "Nung Chan Monastery", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJ9UvPvP6uQjQRq0CCfaWofcY"},
        {"src": "北投5.jpg", "description": "Menghuan Lake", "link": "https://www.google.com/maps/place/%E5%A4%A2%E5%B9%BB%E6%B9%96/@25.1669752,121.5498499,15z/data=!3m1!4b1!4m6!3m5!1s0x3442b26d315ff96f:0x83c0b5426e02c043!8m2!3d25.1667829!4d121.5602805!16s%2Fg%2F11b6_gv9zx?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "北投6.jpg", "description": "Thermal Valley", "link": "https://www.google.com/maps/place/%E5%9C%B0%E7%86%B1%E8%B0%B7/@25.1379192,121.5118813,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ae4248dcbdab:0xe815d42f76dda317!8m2!3d25.137894!4d121.5118863!16s%2Fg%2F155sbbsd?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"}
    ],
    "Songshan": [
        {"src": "松山1.jpg", "description": "Raohe Street Tourist Night Market", "link": "https://www.google.com/maps/place/%E9%A5%92%E6%B2%B3%E8%A1%97%E8%A7%80%E5%85%89%E5%A4%9C%E5%B8%82/@25.0508902,121.5749142,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ab9c0db4a583:0x3da21183815df6f6!8m2!3d25.0508854!4d121.5774891!16s%2Fm%2F03c71n_?hl=zh-tw&entry=ttu&g_ep=EgoyMDI0MTExMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "松山2.jpg", "description": "Xikou (Rainbow) Wharf", "link": "https://www.google.com.tw/maps/place/%E5%BD%A9%E8%99%B9%E7%A2%BC%E9%A0%AD/@25.0514659,121.572292,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ab9bcf268111:0xea9a66c6a5de9f33!8m2!3d25.0514336!4d121.5749295!16s%2Fg%2F1q5bm4fnm?hl=zh-TW&entry=ttu&g_ep=EgoyMDI0MTExMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "松山3.jpg", "description": "Songshan Ciyou Temple", "link": "https://www.google.com/maps/place/%E6%9D%BE%E5%B1%B1%E6%85%88%E7%A5%90%E5%AE%AE/@25.051223,121.5751151,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ab9c6d479ecb:0xe9dd0be65263781!8m2!3d25.0512182!4d121.57769!16s%2Fm%2F03gw98m?hl=zh-tw&entry=ttu&g_ep=EgoyMDI0MTExMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "松山4.jpg", "description": "Taipei Arena", "link": "https://www.google.com/maps/place/%E8%87%BA%E5%8C%97%E5%B0%8F%E5%B7%A8%E8%9B%8B/@25.0506897,121.5475503,17z/data=!3m1!5s0x3442abc29e5461b3:0xb56e2d6766c30a67!4m6!3m5!1s0x3442abe81eb85771:0x682251d5c6f37a58!8m2!3d25.0506849!4d121.5501199!16zL20vMGJyNzd2?entry=ttu&g_ep=EgoyMDI0MTExMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "松山5.jpg", "description": "Taipei Songshan Airport Observation Deck", "link": "https://en.wikipedia.org/wiki/Dadaocheng"},
        {"src": "松山6.jpg", "description": "Liberty Lane and Nylon Cheng Memorial Museum", "link": "https://maps.app.goo.gl/9h2J3aNVM2kEErje8"}   
    ],
    "Xinyi": [
        {"src": "信義1.jpg", "description": "Songshan Cultural and Creative Park", "link": "https://maps.app.goo.gl/z3vMGRSupk31982S8"},
        {"src": "信義2.jpg", "description": "Wufenpu- the garment district", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJC1KFvJirQjQRmS-gn4gGaFs"},
        {"src": "信義3.jpg", "description": "Taipei 101 Mall", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJraeA2rarQjQRPBBjyR3RxKw"},
        {"src": "信義4.jpg", "description": "Nangang Mountain System: Xiangshan (Mt. Elephant) Hiking Trail", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJaQ8C06irQjQRvoQAGN9dOBA"},
        {"src": "信義5.jpg", "description": "Xinyi Assembly Hall,Taipei City", "link": "https://www.google.com/maps/place/%E5%9B%9B%E5%9B%9B%E5%8D%97%E6%9D%91/@25.0315502,121.5593003,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ab0b72cdbb29:0xd60daa5aaa7a938a!8m2!3d25.0315454!4d121.5618806!16s%2Fg%2F11t1f2g53t?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"},
        {"src": "信義6.jpg", "description": "National Sun Yat-sen Memorial Hall", "link": "https://www.google.com/maps/place/%E5%9C%8B%E7%AB%8B%E5%9C%8B%E7%88%B6%E7%B4%80%E5%BF%B5%E9%A4%A8/@25.0400354,121.5576649,17z/data=!3m2!4b1!5s0x3442abc7f32f9ca1:0x21f0a025b9e58c4e!4m6!3m5!1s0x3442a9eec87122c3:0xbe4641f96f0e578a!8m2!3d25.0400306!4d121.5602452!16zL20vMDJybWY4?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"},
 
    ],
    "Nangang": [
        {"src": "南港1.jpg", "description": "POPOP Taipei", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJPfeBBF6rQjQRMzfxD6cSUNQ"},
        {"src": "南港2.jpg", "description": "Old Genliao Hiking Trail", "link": "https://www.google.com/maps/place/%E5%9C%9F%E5%BA%AB%E5%B2%B3%E6%9B%B4%E5%AF%AE%E5%8F%A4%E9%81%93/@25.0254852,121.633369,17z/data=!3m1!4b1!4m6!3m5!1s0x345d54cc1a61364b:0xdf924acd7260ac6e!8m2!3d25.0254852!4d121.633369!16s%2Fg%2F11b7hnzbn3?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "南港3.jpg", "description": "Hu Shih Memorial Hall", "link": "https://maps.app.goo.gl/jHUEAek4ZvAXAfQy7"},
        {"src": "南港4.jpg", "description": "The N24 Ark Taipei", "link": "https://en.wikipedia.org/wiki/Dadaocheng"},
        {"src": "南港5.jpg", "description": "Lishan Farmers Square_Lishan Park", "link": "https://www.google.com.tw/maps/place/%E9%BA%97%E5%B1%B1%E8%BE%B2%E6%B0%91%E5%BB%A3%E5%A0%B4(%E9%BA%97%E5%B1%B1%E5%85%AC%E5%9C%92)/@25.0224212,121.5932736,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ab1cefd29315:0x20dd64076219e542!8m2!3d25.0224212!4d121.5958485!16s%2Fg%2F11bz_1s5rw?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "南港6.jpg", "description": "Songshan Sanatorium Director’s Dormitory", "link": "https://www.google.com.tw/maps/place/%E6%9D%BE%E5%B1%B1%E7%99%82%E9%A4%8A%E6%89%80%E6%89%80%E9%95%B7%E5%AE%BF%E8%88%8D%EF%BC%88%E9%9D%9C%E5%BF%83%E8%8B%91-%E7%99%82%E7%99%92%E5%8F%A4%E8%B9%9F%EF%BC%89/@25.048481,121.5909181,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ab71d259f459:0xc3516b897da9151a!8m2!3d25.048481!4d121.593493!16s%2Fg%2F11hbljvnn1?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"} 
    ],
    "Wanhua": [
        {"src": "萬華1.jpg", "description": "Huaxi Street Tourist Night Market", "link": "https://www.google.com/maps/place/%E8%87%BA%E5%8C%97%E8%8F%AF%E8%A5%BF%E8%A1%97%E5%A4%9C%E5%B8%82/@25.0386036,121.4958623,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a9a940c8f96b:0x6aee182d28c2fb39!8m2!3d25.0385988!4d121.4984426!16s%2Fm%2F0bh6ykr?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"},
        {"src": "萬華2.jpg", "description": "Lungshan Temple", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJCd7n16ipQjQRihzEWF4z6Pg"},
        {"src": "萬華3.jpg", "description": "Ximending", "link": "https://www.google.com/maps/place/%E8%A5%BF%E9%96%80%E7%94%BA%E5%BE%92%E6%AD%A5%E5%8D%80/@25.0440478,121.5047406,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a909415dc0bb:0x3f5445181a0c0cc8!8m2!3d25.044043!4d121.5073209!16s%2Fg%2F11ddzhps9r?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"},
        {"src": "萬華4.jpg", "description": "Heritage and Culture Education Center of Taipei (the historic Bopiliao area )", "link": "https://www.google.com/maps/place/%E5%89%9D%E7%9A%AE%E5%AF%AE%E6%AD%B7%E5%8F%B2%E8%A1%97%E5%8D%80/@25.0368428,121.4995845,17z/data=!3m1!4b1!4m6!3m5!1s0x3442a9a8d017b6dd:0xff3361bbadd40fe9!8m2!3d25.036838!4d121.5021648!16s%2Fg%2F155r2_r7?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"},
        {"src": "萬華5.jpg", "description": "Tianhou Temple", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJbSR3CAmpQjQRaGSNghiSyrw"},
        {"src": "萬華6.jpg", "description": "U-mkt", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJN4_GsqipQjQRZMMAKGYy86U"} 
    ],
    "Wenshan": [
        {"src": "文山1.jpg", "description": "Maokong Gondola", "link": "https://www.google.com/maps/place/%E8%B2%93%E7%A9%BA%E7%BA%9C%E8%BB%8A/@24.9959561,121.5737527,17z/data=!3m2!4b1!5s0x3442aa66b717cec7:0x6257b921976f4e25!4m6!3m5!1s0x3442aa8b314e950f:0xf35a322ce7005cc1!8m2!3d24.9959513!4d121.576333!16s%2Fg%2F11c2kk1ksy?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"},
        {"src": "文山2.jpg", "description": "Taipei Zoo", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJj4EySmCqQjQRZte0Cf0G_qo"},
        {"src": "文山3.jpg", "description": "140 Height Park", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJj4EySmCqQjQRZte0Cf0G_qo"},
        {"src": "文山4.jpg", "description": "Taipei Tea Promotion Center for Tie Guanyin Tea and Baozhong Tea", "link": "https://www.google.com/maps/place/140%E9%AB%98%E5%9C%B0%E5%85%AC%E5%9C%92/@25.0042889,121.5666126,17z/data=!3m1!4b1!4m6!3m5!1s0x3442aa427a22cef1:0x59269cdcefc3d1fa!8m2!3d25.0042889!4d121.5666126!16s%2Fg%2F11cn31n1gc?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "文山5.jpg", "description": "The Wall Live House", "link": "https://www.google.com/maps/place/THE+WALL+LIVE+HOUSE/@25.0107881,121.5341948,17z/data=!3m2!4b1!5s0x3442a9f55859d65f:0xab332151acc01c77!4m6!3m5!1s0x3442a9f5585f9f09:0x8c72211550e38b60!8m2!3d25.0107833!4d121.5367751!16s%2Fg%2F11d_ynby7j?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"},
        {"src": "文山6.jpg", "description": "U Theatre on the Mountain", "link": "https://www.google.com/maps/place/%E5%84%AA%E4%BA%BA%E7%A5%9E%E9%BC%93%E5%B1%B1%E4%B8%8A%E5%8A%87%E5%A0%B4/@24.9658551,121.5712173,17z/data=!3m1!4b1!4m6!3m5!1s0x346801cf2b52a449:0x642c95ce33b6175!8m2!3d24.9658503!4d121.5737976!16s%2Fg%2F11ckxkd6b0?entry=ttu&g_ep=EgoyMDI0MTExMy4xIKXMDSoJLDEwMjExMjM0SAFQAw%3D%3D"}
    ],
    "Neihu": [
        {"src": "內湖1.jpg", "description": "Taipei Flower Market", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJcQIe-IarQjQR9oTmYtKD5xg"},
        {"src": "內湖2.jpg", "description": "Dahu Park", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJcQIe-IarQjQR9oTmYtKD5xg"},
        {"src": "內湖3.jpg", "description": "White Stone Cirque Agri-tourism Area_Neihu Strawberry Festival", "link": "https://www.google.com/maps/place/%E7%99%BD%E7%9F%B3%E6%B9%96%E4%BC%91%E9%96%92%E8%BE%B2%E6%A5%AD%E5%8D%80%E7%99%BC%E5%B1%95%E5%8D%94%E6%9C%83/@25.1051282,121.5920456,17z/data=!3m1!4b1!4m6!3m5!1s0x3442adbc7057c03b:0xea286073a3c95628!8m2!3d25.1051282!4d121.5920456!16s%2Fg%2F11g24ny_3r?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"},
        {"src": "內湖4.jpg", "description": "Wuzhi Mountain System: Jinmianshan Hiking Trail", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJp6s0vUWsQjQRLocNbrRbuqA"},
        {"src": "內湖5.jpg", "description": "Yuanjue Waterfall", "link": "https://www.google.com/maps/search/?api=1&query=%20&query_place_id=ChIJlzveTiCtQjQRSWENWLphijY"},
        {"src": "內湖6.jpg", "description": "Guo Ziyi Memorial Hall_Neihu Red House", "link": "https://www.google.com/maps/place/%E9%83%AD%E5%AD%90%E5%84%80%E7%B4%80%E5%BF%B5%E5%A0%82/@25.0796293,121.5865772,17z/data=!4m6!3m5!1s0x3442ac62513a1c69:0x32431116595d5259!8m2!3d25.0796293!4d121.5865772!16s%2Fg%2F11b5qdb4fb?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"}
    ],
    # 可在此擴展更多地區及圖片
}

###千瑜食物部分
# Load data from CSV files
data_snacks = pd.read_csv("data/美食資料集/台灣小吃推薦TOP5.csv")
data_food = pd.read_csv("data/美食資料集/美食聲量圖TOP5.csv")
data_beverages = pd.read_csv("data/美食資料集/飲料聲量圖TOP5.csv")

# Reshape the data to fit the required format
data_snacks = data_snacks.melt(var_name="Item", value_name="Count").sort_values(by="Count", ascending=True)
data_food = data_food.melt(var_name="Restaurant", value_name="Count").sort_values(by="Count", ascending=True)
data_beverages = data_beverages.melt(var_name="Brand", value_name="Count").sort_values(by="Count", ascending=True)

# Create a dictionary mapping categories to images with links and descriptions
category_images = {
    "snacks": [
        {"src": "/assets/珍珠奶茶_1.jpg", "link": "https://reurl.cc/96W3XO", "description": "Bubble tea"},
        {"src": "/assets/臭豆腐2.jpg", "link": "https://reurl.cc/mRpyL7", "description": "Stinky tofu"},
        {"src": "/assets/滷肉飯.jpg", "link": "https://reurl.cc/eGpy3Q", "description": "Braised pork on rice"},
        {"src": "/assets/鹹酥雞.jpg", "link": "https://reurl.cc/V02M1y", "description": "Taiwanese fried chicken"},
        {"src": "/assets/蚵仔煎.jpg", "link": "https://reurl.cc/qnpvZy", "description": "Oyster omelette"}
    ],
    "food": [
        {"src": "/assets/1富錦樹_1182X1182.png", "link": "https://guide.michelin.com/tw/en/taipei-region/taipei/restaurant/fujin-tree-taiwanese-cuisine-champagne-songshan", "description": "Fujin Tree"},
        {"src": "/assets/2頤宮_1075X1075.jpg", "link": "https://www.palaisdechinehotel.com/pdc_en/pages/26/0/66", "description": "Le Palais"},
        {"src": "/assets/3RAW_1076X1076.jpg", "link": "https://www.raw.com.tw/en", "description": "RAW"},
        {"src": "/assets/4請客樓_842X842.jpg", "link": "https://www.theguesthouserestaurant.com/all-day-menu/", "description": "The Guest House"},
        {"src": "/assets/5米香_1075X1075.jpg", "link": "https://www.grandmayfull.com/dining/MIPON", "description": "Grand Mayfull Hotel_MIPON"}
    ],
    "beverages": [
        {"src": "/assets/1Natural First_2048X2048.jpg", "link": "https://bilingualshop.cdri.org.tw/en/xmdoc/cont?xsmsid=0L279505338834816834&sid=0L279507062435269473", "description": "Natural First"},
        {"src": "/assets/2KEBUKE_1811X1811.jpg", "link": "https://kebuke.com/en/product/", "description": "KEBUKE"},
        {"src": "/assets/3CoCo_1161X1161.jpg", "link": "https://www.coco-tea.com/Products", "description": "CoCo"},
        {"src": "/assets/450lan_300X300.jpg", "link": "https://www.yelp.com/biz/50%E5%B5%90-%E8%90%AC%E8%8F%AF%E5%8D%80", "description": "50lan"},
        {"src": "/assets/5chingshin_720X720.jpg", "link": "https://scontent.fkhh3-1.fna.fbcdn.net/v/t1.6435-9/82624873_2681952548700484_1270572027622719488_n.jpg?_nc_cat=102&ccb=1-7&_nc_sid=0b6b33&_nc_ohc=WJnkGm_uPSEQ7kNvgG8FdhI&_nc_zt=23&_nc_ht=scontent.fkhh3-1.fna&_nc_gid=A-oD6Ri_ej8Ysyun1ygxcRD&oh=00_AYC4ihaB1KhGx8EtDMHdyLg_w7SLXbwRB1vB4w4r3d23HA&oe=679F2DCB", "description": "Chingshin"}
    ]
}

###學長地圖
# 加載 Shapefile 並合併行政區（TOWNNAME）的資料
shapefile_path = "data/VILLAGE_NLSC_1131128_updated.shp"
gdf = gpd.read_file(shapefile_path)

# 確保 CRS 為 WGS84 (EPSG:4326)
if gdf.crs is None:
    gdf.set_crs(epsg=4326, inplace=True)
else:
    gdf = gdf.to_crs(epsg=4326)

# 將幾何類型處理為單部分幾何
gdf = gdf.explode(index_parts=True)

# 過濾台北市的行政區
taipei_gdf = gdf[gdf["COUNTYNAME"] == "臺北市"]

# 保留必要的欄位
taipei_gdf = taipei_gdf[["TOWNNAME", "geometry"]]

# 按 TOWNNAME 合併
town_gdf = taipei_gdf.dissolve(by="TOWNNAME", as_index=False, aggfunc="first")


# 將合併後的 GeoDataFrame 轉為 GeoJSON
town_geojson = json.loads(town_gdf.to_json())

highlight_style = {
    "color": "#cd355c",
    "weight": 3,
    "opacity": 1.0,
    "fillOpacity": 0.5
}

default_style = {
    "color": "#314572",
    "weight": 1,
    "opacity": 0.5,
    "fillOpacity": 0.2
}

# 為每個 Feature 設置初始樣式與 Tooltip
for feature in town_geojson["features"]:
    feature["properties"]["style"] = default_style
    feature["properties"]["tooltip"] = feature["properties"]["TOWNNAME"]

# 地圖上的景點資料
famous_spots = {
    "Taipei101": {
        "name": "Taipei 101",
        "coordinates": [25.0339, 121.5645],
        "place_id": "ChIJH56c2rarQjQRphD9gvC8BhI"
    },
    "SongshanCreativePark": {
        "name": "Songshan Cultural and Creative Park",
        "coordinates": [25.0443, 121.5584],
        "place_id": "ChIJO0vOI7-rQjQR3Pl9_4cPK8g"

    },
    "YangmingPark": {
        "name": "Yangming Park",
        "coordinates": [25.1651, 121.5531],
        "place_id": "ChIJD-Zgfv-tQjQRz9pBzuQt0yw"
    },
    "Huashan1914CreativePark": {
        "name": "Huashan 1914 Creative Park",
        "coordinates": [25.0451, 121.5296],
        "place_id": "ChIJbSTgI2WpQjQRcVwWB2cnyfE"
    },
    "ChiangKaiShekMemorialHall": {
        "name": "National Chiang Kai-shek Memorial Hall",
        "coordinates": [25.0342, 121.5215],
        "place_id": "ChIJTamiuZ2pQjQRsmnfkkID6UM"
    },
    "TaipeiZoo": {
        "name": "Taipei Zoo",
        "coordinates": [24.9987, 121.5812],
        "place_id": "ChIJj4EySmCqQjQRZte0Cf0G_qo"
    },
    "NationalTaiwanScienceEducationCenter": {
        "name": "National Taiwan Science Education Center",
        "coordinates": [25.0896, 121.5184],
        "place_id": "ChIJ42fAy7iuQjQRE2DgdH7p7fQ"
    },
    "NationalPalaceMuseum": {
        "name": "National Palace Museum",
        "coordinates": [25.1023, 121.5485],
        "place_id": "ChIJfUpAzTqsQjQRwQl6ORhwbV0"
    },
    "NationalDrSunYatSenMemorialHall": {
        "name": "National Dr. Sun Yat-sen Memorial Hall",
        "coordinates": [25.0402, 121.5605],
        "place_id": "ChIJwyJxyO6pQjQRilcOb_lBRr4"
    },
    "TaipeiChildrensAmusementPark": {
        "name": "Taipei Children's Amusement Park",
        "coordinates": [25.0853, 121.5217],
        "place_id": "ChIJG9qGWr-uQjQRR1iXVOTfVl8"
    },
    "TaipeiBotanicalGarden": {
        "name": "Taipei Botanical Garden",
        "coordinates": [25.0325, 121.5090],
        "place_id": "ChIJe1ASN0-pQjQRIeghXqXkkAg"
    },
    "TaipeiAstronomicalMuseum": {
        "name": "Taipei Astronomical Museum",
        "coordinates": [25.0952, 121.5152],
        "place_id": "ChIJl8eBsL6uQjQRwwn6OA2ejxI"
    },
    "NationalTaiwanMuseum": {
        "name": "National Taiwan Museum",
        "coordinates": [25.0451, 121.5155],
        "place_id": "ChIJZVl9mw2pQjQRNl7qT3nVk80"
    },
    "TaipeiFineArtsMuseum": {
        "name": "Taipei Fine Arts Museum",
        "coordinates": [25.0726, 121.5247],
        "place_id": "ChIJ-ffZ_VGpQjQRcaEDDIjDQHo"
    }
}

dl.LayerGroup(
    id="markers",
    children=[
        dl.Marker(
            position=spot["coordinates"],
            children=[
                dl.Tooltip(spot["name"]),
                dl.Popup(html.Div([html.H3(spot["name"])]))
            ]
        )
        for spot in famous_spots.values()
    ]
)

# 穿搭圖
season_images = {
    "Spring": "assets/穿瘩_春.png",
    "Summer": "assets/穿瘩_夏.png",
    "Autumn": "assets/穿瘩_秋.png",
    "Winter": "assets/穿瘩_冬.png"
}

# 行程建議
day_to_images = {
    "Cultural and Creative Itinerary": "assets/台灣文創.png",
    "Local Architectural Highlights Itinerary": "assets/台灣建築.png",
    "Nature Itinerary": "assets/台灣溫泉.png"
}

####################################################################

# 初始化應用程式
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='G5 Travel Data Analysis Dashboard', suppress_callback_exceptions=True)
server = app.server

# 外觀設定
tab_style = {
    'idle':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'backgroundColor': '#deb522',
        'border':'none'
    },
    'active':{
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display':'flex',
        'alignItems':'center',
        'justifyContent':'center',
        'fontWeight': 'bold',
        'border':'none',
        'textDecoration': 'underline',
        'backgroundColor': '#deb522'
    }
}

MAX_OPTIONS_DISPLAY = 3200

app.layout = html.Div([
    dbc.Container([
        # 圖片區域
        dbc.Row(
            html.Div(
                children=[
                    html.Img(
                        src="assets/整個首頁.png",  # 替換為你的圖片路徑
                        style={
                            "width": "100%",  # 寬度填滿整個螢幕
                            "height": "auto",  # 保持圖片比例
                            "display": "block",  # 移除圖片下方的多餘空白
                        }
                    ),
                    # Tab 按鈕，位置設為絕對，讓它顯示在圖片上方
                    dbc.Row([
                        dbc.Col(
                            dcc.Tabs(
                                id='graph-tabs', 
                                value='overview', 
                                children=[
                                    dcc.Tab(
                                        label='Weather', 
                                        value='weather', 
                                        style={**tab_style['idle'], 
                                               'backgroundColor': 'rgba(255, 255, 255, 0)', 
                                               'fontFamily': 'Brush Script MT', 
                                               'fontSize': '50px', 
                                               'color': 'white',
                                               'marginRight': '0px'}, 
                                        selected_style={**tab_style['active'], 
                                                        'backgroundColor': 'rgba(255, 255, 255, 0)',
                                                        'fontFamily': 'Brush Script MT', 
                                                        'fontSize': '50px',
                                                        'color': 'white',
                                                        'marginRight': '0px'}),
                                    dcc.Tab(
                                        label='Attractions', 
                                        value='attractions', 
                                        style={**tab_style['idle'], 
                                               'backgroundColor': 'rgba(255, 255, 255, 0)', 
                                               'fontFamily': 'Brush Script MT', 
                                               'fontSize': '50px', 
                                               'color': 'white',
                                               'marginLeft': '30px'}, 
                                        selected_style={**tab_style['active'], 
                                                        'backgroundColor': 'rgba(255, 255, 255, 0)',
                                                        'fontFamily': 'Brush Script MT', 
                                                        'fontSize': '50px',
                                                        'color': 'white',
                                                        'marginLeft': '30px'}),
                                    dcc.Tab(
                                        label='Foods', 
                                        value='foods', 
                                        style={**tab_style['idle'], 
                                               'backgroundColor': 'rgba(255, 255, 255, 0)', 
                                               'fontFamily': 'Brush Script MT', 
                                               'fontSize': '50px', 
                                               'color': 'white',
                                               'marginLeft': '20px'}, 
                                        selected_style={**tab_style['active'], 
                                                        'backgroundColor': 'rgba(255, 255, 255, 0)',
                                                        'fontFamily': 'Brush Script MT', 
                                                        'fontSize': '50px',
                                                        'color': 'white',
                                                        'marginLeft': '20px'}),
                                    dcc.Tab(
                                        label='Suggestions', 
                                        value='suggestions', 
                                        style={**tab_style['idle'], 
                                               'backgroundColor': 'rgba(255, 255, 255, 0)',
                                               'fontFamily': 'Brush Script MT', 
                                               'fontSize': '48px', 
                                               'color': 'white',
                                               'marginLeft': '10px',
                                               'marginRight': '40px'}, 
                                        selected_style={**tab_style['active'], 
                                                        'backgroundColor': 'rgba(255, 255, 255, 0)',
                                                        'fontFamily': 'Brush Script MT', 
                                                        'fontSize': '50px',
                                                        'color': 'white',
                                                        'marginLeft': '10px',
                                                        'marginRight': '40px'}),
                                ], 
                                style={'height': '160px', 'position': 'absolute', 'top': '650px', 'left': "34px", 'width': '80%'}
                            ),
                            width=15  # 控制 Tab 的寬度
                        )
                    ]), 

                ],
                style={
                    "position": "relative",  # 使容器成為相對定位
                    "width": "100%",  # 父容器寬度填滿
                    "padding": "0px"  # 移除內部間距
                }
            )
        ),
        # 用於顯示不同頁面的內容
        html.Div(id='graph-content')

    ], fluid=True, style={'padding': '0px'})  # 設置 Container 為 fluid 並移除內間距
], style={'backgroundColor': 'white', 'minHeight': '100vh'})



# 根據選擇的標籤頁更新顯示的內容
@app.callback(
    Output('graph-content', 'children'),
    [Input('graph-tabs', 'value')]
)
def render_tab_content(tab):
    if tab == 'weather':
        # 返回 'weather' 頁面的佈局
        return html.Div([    
            # 第一排下拉選單 - 長條圖(Col1) & 折線圖(Col2)
            dbc.Row([
                dbc.Col([
                    html.H3("Taipei City Monthly Precipitation ", 
                            style={'color': '#314572', 
                                   'margin-top': '5px'}),
                    html.Label("Please select a category:", 
                            style={'color': '#314572', 
                                   'fontSize': '20px',
                                   'margin-top': '5px'}),
                    dcc.Dropdown(
                        id='category-dropdown-bar',
                        options=[
                            {'label': category, 'value': category} for category in category_list],
                        value=category_list[0],
                        clearable=False,
                        style={
                            'backgroundColor': 'white',  # 設置背景顏色
                            'color': 'black',  # 設置字體顏色
                            'fontSize': '16px',  # 設置字體大小
                            'border': '1px solid #deb522',  # 設置邊框顏色
                            'borderRadius': '5px',  # 設置圓角邊框
                        }),
                ], style={'paddingLeft': '70px',
                          "backgroundColor": "#efebe3",
                          'margin-top': '5px'}),

                dbc.Col([
                    html.H3("Taipei City monthly temperature ", 
                            style={'color': '#314572', 
                                   'margin-top': '5px'}),
                    html.Label("Please select a category:", 
                               style={'color': '#314572',
                                      'fontSize': '20px',
                                      'margin-top': '5px'}),
                    dcc.Dropdown(
                        id='category-dropdown-line',
                        options = [
                           {'label': category, 'value': category} for category in temperature_df['Category'].unique()
                        ],
                        value=temperature_df['Category'].unique()[0],
                        clearable=False,
                        style={
                            'backgroundColor': 'white',  # 設置背景顏色
                            'color': 'black',  # 設置字體顏色
                            'fontSize': '16px',  # 設置字體大小
                            'border': '1px solid #deb522',  # 設置邊框顏色
                            'borderRadius': '5px',  # 設置圓角邊框
                        }),
                ], style={'paddingRight': '70px',
                          'backgroundColor': '#efebe3',
                          'margin-top': '5px'}),
            ]),
            # 第一排圖表顯示區 - 長條圖(Col1：tabs-content-1) & 折線圖(Col2：tabs-content-2)
            dbc.Row([
                dbc.Col([
                    dcc.Loading([
                        html.Div(id='tabs-content-1'),
                    ],
                    type='default',color='#efebe3'),
                ], style={'paddingLeft': '70px',
                          'margin-top': '10px',
                          'color':'#efebe3'
                          }),
                dbc.Col([
                    dcc.Loading([
                        html.Div(id='tabs-content-2'),
                    ],
                    type='default',color='#deb522'),
                ], style={'paddingRight': '70px',
                          'margin-top': '10px'}),
            ], style={'backgroundColor': '#efebe3','margin-bottum': '15px'}),

        # 第二排下拉選單 - 長條圖(Col1) & 折線圖(Col2)
            dbc.Row([
                dbc.Col([
                    html.H3("Taipei City Average Duration of Daylight ", 
                            style={'color': '#314572', 
                                   'margin-top': '15px'}),
                    html.Label("Please select a category:", 
                                style={'color': '#314572',
                                      'fontSize': '20px',
                                      'margin-top': '5px'}),
                    dcc.Dropdown(
                        id='category-dropdown-bar2',
                        options=[
                            {'label': category, 'value': category} for category in category_list_lightduration],
                        value=category_list_lightduration[0],
                        clearable=False,
                        style={
                            'backgroundColor': 'white',  # 設置背景顏色
                            'color': 'black',  # 設置字體顏色
                            'fontSize': '16px',  # 設置字體大小
                            'border': '1px solid #deb522',  # 設置邊框顏色
                            'borderRadius': '5px',  # 設置圓角邊框
                        }),
                ], style={'paddingLeft': '70px',
                          'backgroundColor': '#efebe3'}),

                dbc.Col([
                    html.H3("Taipei City Sunrise & Sunset Time ", 
                            style={'color': '#314572', 
                                   'margin-top': '15px'}),
                    html.Label("Please select a category:", 
                                style={'color': '#314572',
                                      'fontSize': '20px',
                                      'margin-top': '5px'}),
                    dcc.Dropdown(
                        id='category-dropdown-line2',
                        options = [
                           {'label': category, 'value': category} for category in suntime_df['Category'].unique()
                        ],
                        value=suntime_df['Category'].unique()[0],
                        clearable=False,
                        style={
                            'backgroundColor': 'white',  # 設置背景顏色
                            'color': 'black',  # 設置字體顏色
                            'fontSize': '16px',  # 設置字體大小
                            'border': '1px solid #deb522',  # 設置邊框顏色
                            'borderRadius': '5px',  # 設置圓角邊框
                        }),
                ], style={'paddingRight': '70px',
                          'backgroundColor': '#efebe3'}),
            ]),
            # 第二排圖表顯示區 - 長條圖(Col3：tabs-content-3) & 折線圖(Col4：tabs-content-4)
            dbc.Row([
                dbc.Col([
                    dcc.Loading([
                        html.Div(id='tabs-content-3'),
                    ],
                    type='default',color='#deb522'),
                ], style={'paddingLeft': '70px',
                          'margin-top': '10px'}),
                
                dbc.Col([
                    dcc.Loading([
                        html.Div(id='tabs-content-4'),
                    ],
                    type='default',color='#deb522'),
                ], style={'paddingRight': '70px',
                          'margin-top': '10px'}),
            ], style={'backgroundColor': '#efebe3'}),      
    
            # 增加頁尾空間
                html.Div(
                    style={'height': '100px'}
                ),
            ], style={'backgroundColor': '#efebe3'})  # 設置整頁背景顏色
    
    elif tab == 'attractions':
    # 標題部分
        return html.Div([
            html.Div([
                html.H3(
                    "Taipei Tourist Attractions",
                    style={
                        "textAlign": "left",
                        "fontWeight": "#314572",
                        "fontStyle": "Big John",
                        "color": "#314572",
                        "marginBottom": "5px"
                    }
                )
             ], style={"backgroundColor": "#efebe3", 
                       "paddingLeft": "70px"}),

    # 文字雲部分
    html.Div(
        html.Img(
            src=wordcloud_image,
            style={
                "width": "100%",
                "long" :"10%",
                "display": "block",
                "border": "3px solid #314572",  # 添加邊框
                "borderRadius": "15px"       # 圓角邊框
            }
        ),
        style={"padding": "20px", 
               "backgroundColor": '#efebe3', 
               "textAlign": "left",
               "paddingLeft":'65px',
               "paddingRight":'65px'}
    ),
            dbc.Row([
                dbc.Col([
                    # 地圖選單
                    html.Div([
                        html.H3("Where do you want to go today?", 
                        style={"marginBottom": "20px",
                            "color":"#314572",
                            "paddingLeft":'70px'}),
                        dl.Map(
                            bounds=[gdf.total_bounds[[1, 0]], gdf.total_bounds[[3, 2]]],
                            zoomControl=True,
                            center=[25.054, 121.565],  # 台北市的中心座標
                            zoom=12,
                            scrollWheelZoom=False,  # 禁用滾輪縮放
                            children=[
                                dl.GeoJSON(
                                    id="geojson",
                                    data=town_geojson,
                                    options=dict(clickable=True),
                                    zoomToBounds=True,
                                    style=default_style,  # 若需要預設樣式
                                    hoverStyle=highlight_style  # 若需要 hover 時樣式變化
                                ),
                                dl.LayerGroup(  # 新增景點標記
                                    id="markers",
                                    children=[
                                        dl.Marker(
                                            position=spot["coordinates"],
                                            children=[
                                                dl.Tooltip(spot["name"]),
                                                dl.Popup( html.Div([
                                                    html.H3(spot["name"]),
                                                    html.P("Click the link to open Google Maps:"),
                                                    html.A(
                                                        "Open in Google Maps",
                                                        href=(
                                                        f"https://www.google.com/maps/search/?api=1&query=%20&query_place_id="
                                                        f"{spot['place_id']}"),
                                                        target="_blank",
                                                        style={"color": "blue", "textDecoration": "underline"}
                        )
                    ])
                )
                                            ]
                                        )
                                        for spot in famous_spots.values()
                                    ]
                                )
                            ],
                            style={"backgroundColor": "#efebe3","height": "90vh", "width": "100%"},
                        ),
                        # 點擊後顯示的區域名稱
                        html.Div(id="selected-region", style={"margin-top": "10px", "font-size": "18px", "font-weight": "bold"}),
        ]),
                dbc.Col([
                # 下拉選單
                html.Div([
                    html.H3("Choose a dist:", 
                            style={
                                    "color": "#314572", 
                                    "marginTop": "10px"}),
                    dcc.Dropdown(
                        id="location-dropdown",
                        options=[{"label": key, "value": key} for key in locations.keys()],
                        value="Shilin",  # 初始值設為空
                        style={
                            'backgroundColor': 'white',  # 設置背景顏色
                            'color': 'black',  # 設置字體顏色
                            'fontSize': '16px',  # 設置字體大小
                            'border': '1px solid #deb522',  # 設置邊框顏色
                            'borderRadius': '5px',  # 設置圓角邊框
                            })
                ],style={"backgroundColor": "#efebe3"}),
            ],style={"paddingLeft":'70px',
                     "paddingRight":'70px'
                     }),

            # 圖片顯示部分
            html.Div(
                id="image-container",
                style={
                    "marginTop": "20px",
                    "textAlign": "center",
                    "backgroundColor": "#efebe3",  # 背景色改為橘色
                    "padding": "30px",
                    "width": "100%",}
            ),
            ]),
        ]),

        # 增加頁尾空間
        html.Div(
            style={'height': '100px'}
                    ),
                ], style={'backgroundColor': '#efebe3'}) # 設置整頁背景顏色
    
    elif tab == 'foods':
    # 標題部分
        return html.Div([
    html.Div([
        html.H3("Taiwanese Food", 
                style={ "fontWeight": "bold",
                        "color": "#314572",
                        "textAlign": "left",
                        "fontStyle": "Big John",
                        "paddingLeft":'70px' }),
    ], style={"backgroundColor": "#efebe3"}),

    html.Div([
        html.Div([
            html.Label("Please choose a kind of food:", 
                            style={'color': '#314572', 
                                   'fontSize': '20px',
                                   'margin-top': '5px'}),
            dcc.Dropdown(
                id="data-dropdown",
                options=[
                    {"label": "Food", "value": "food"},
                    {"label": "Snacks", "value": "snacks"},
                    {"label": "Beverages", "value": "beverages"},
                ],
                value="food",  # Default to "food"
                style={
                            'backgroundColor': 'white',  # 設置背景顏色
                            'color': 'black',  # 設置字體顏色
                            'fontSize': '16px',  # 設置字體大小
                            'border': '1px solid #deb522',  # 設置邊框顏色
                            'borderRadius': '5px',  # 設置圓角邊框
                        }
            )
        ],style={"paddingRight": "70px"}),

        html.Div(id="graph-container", style={
            "width": "100%",
            "marginLeft": "0px",
            "marginRight": "auto",
            "display": "block",
            "paddingRight": "70px",
            'margin-top': '10px'
        }),

        # Add a title above the image section
        html.H3(" Top 5 Brand ", style={
            "fontSize": "30px",
            "fontWeight": "bold",
            "color": "#314572",
            "textAlign": "left",
            "marginTop": "15px",
            "marginBottom": "15px",
            "fontStyle": "Big John"
        }),

        html.Div(id="image-container2", style={
            "marginTop": "10px",
            "textAlign": "left",
            "backgroundColor": "#efebe3"
        })
    ], style={"marginBottom": "20px",
              "paddingLeft": "70px",
              "backgroundColor": "#efebe3"}),
              
        # 增加頁尾空間
        html.Div(
            style={'height': '100px'}
                    ),
                ], style={'backgroundColor': '#efebe3'}) # 設置整頁背景顏色
    
    elif tab == 'suggestions':
            return html.Div([
            # 標題部分
            html.Div([
                html.H3("Travel suggestions", 
                        style={"color": "#314572",
                               "textAlign": "left",
                               "fontStyle": "Big John"}),
            ], style={"marginBottom": "20px",
                      "paddingLeft": "70px",
                      "backgroundColor": "#efebe3"}),

            # 左右分欄布局
            dbc.Row(
                [dbc.Col(
                html.Div([
                    html.H3("Which month will you start exploring Taipei?", 
                            style={'margin-top': '5px',
                                    "color": "#314572", 
                                    "marginBottom": "10px",
                                    "backgroundColor": "#efebe3"}),  
                    dcc.Dropdown(
                        id="season-dropdown",
                        options=[{"label": month, "value": month} for month in month_order],  # 使用月份的順序
                        value="Jan",  # 預設為一月
                        style={
                                'backgroundColor': 'white',  # 設置背景顏色
                                'color': 'black',  # 設置字體顏色
                                'fontSize': '16px',  # 設置字體大小
                                'border': '1px solid #deb522',  # 設置邊框顏色
                                'borderRadius': '5px',  # 設置圓角邊框
                            }
                    ),
                    html.Div(
                                id="weather-info",
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "alignItems": "top",  # 垂直居中
                                    "justifyContent": "left",  # 水平居中
                                    "height": "100%",  # 填滿可用高度
                                    "marginTop": "60px",
                                    "borderRadius": "15px"
                                },
                            ),
                ])
            ),
                dbc.Col(
                        html.Div(
                            id="season-image",
                            style={
                                'margin-top': '5px',
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",  # 垂直居中
                                "justifyContent": "center",  # 水平居中
                                "height": "100%",  # 填滿可用高度
                                "borderRadius": "15px",
                            },
                        ),
                    ),
                ],
                style={"marginTop": "20px",
                       "marginBottum": "20px",
                       "backgroundColor": "#efebe3",
                       "paddingLeft": "70px",
                       "paddingRihgt": "70px"},
            ),
            # 新增的天數篩選器和圖片顯示部分
        html.Div([
            html.H3("Select your travel type:", 
                    style={"color": "#314572", 
                           "marginBottom": "10px"}),  
            dcc.Dropdown(
                id="day-dropdown",
                options=[
                    {"label": "Cultural and Creative Itinerary", "value": "Cultural and Creative Itinerary"},
                    {"label": "Local Architectural Highlights Itinerary", "value": "Local Architectural Highlights Itinerary"},
                    {"label": "Nature Itinerary", "value": "Nature Itinerary"}
                ],
                value="Cultural and Creative Itinerary",  # 預設為 1 天
                style={
                            'backgroundColor': 'white',  # 設置背景顏色
                            'color': 'black',  # 設置字體顏色
                            'fontSize': '16px',  # 設置字體大小
                            'border': '1px solid #deb522',  # 設置邊框顏色
                            'borderRadius': '5px',  # 設置圓角邊框
                        }
            ),
            html.A(
                "🔗 Route from Google Maps",
                id="dynamic-link",
                href="https://www.google.com/maps/dir/%E5%8F%B0%E5%8C%97%E8%BB%8A%E7%AB%99/100%E5%8F%B0%E5%8C%97%E5%B8%82%E4%B8%AD%E6%AD%A3%E5%8D%80%E5%85%AB%E5%BE%B7%E8%B7%AF%E4%B8%80%E6%AE%B51%E8%99%9F%E8%8F%AF%E5%B1%B11914%E6%96%87%E5%8C%96%E5%89%B5%E6%84%8F%E7%94%A2%E6%A5%AD%E5%9C%92%E5%8D%80/@25.0487963,121.5138317,15.21z/data=!4m16!4m15!1m5!1m1!1s0x3442a972a8266295:0xece39c57ea7e4e12!2m2!1d121.51375!2d25.04882!1m5!1m1!1s0x3442a96523e0246d:0xf1c9276707165c71!2m2!1d121.5293583!2d25.0440698!2m1!5e1!3e3?authuser=0&entry=ttu&g_ep=EgoyMDI1MDEwMS4wIKXMDSoASAFQAw%3D%3D",
                target="_blank",
                style={"marginLeft": "20px", "fontSize": "18px", "color": "brown", "textDecoration": "underline", "display": "inline-block"}
            ),
            html.Div(id="day_to_images", style={
                "marginTop": "20px",
                "padding": "20px",
                "textAlign": "center",
                "backgroundColor": "#efebe3"
            })
        ],style={"paddingLeft": "70px","paddingRihgt": "70px"}),      

        # 增加頁尾空間
        html.Div(
            style={'height': '100px'}
                    ),
                ], style={'backgroundColor': '#efebe3'}) # 設置整頁背景顏色

    else:
        return html.Div("選擇的標籤頁不存在。", style={'color': 'white'})

# 長條圖降雨量回調
@app.callback(
    Output('tabs-content-1', 'children'),
    [Input('category-dropdown-bar', 'value'),
     Input('graph-tabs', 'value')]
)
def update_precipitation_bar_chart(selected_category, tab):
    if tab != 'weather':
        return no_update
    # Filter the dataset for the selected category
    filtered_df = precipitation_df[precipitation_df['Category'] == selected_category]

    # Create the bar chart
    fig = px.bar(
        filtered_df, 
        x='Month', 
        y='Precipitation', 
        title=f'Precipitation for {selected_category}')
    fig.update_traces(marker=dict(color='#314572'))
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the plot area
        paper_bgcolor='#f5f5f5'  # Light grey background for the whole chart
    )
    return dcc.Graph(id='graph1', figure=fig)

# 長條圖平均日照回調
@app.callback(
    Output('tabs-content-3', 'children'),
    [Input('category-dropdown-bar2', 'value'),
     Input('graph-tabs', 'value')]
)
def update_lightduration_chart(selected_category, tab):
    if tab != 'weather':
        return no_update
    # Filter the dataset for the selected category
    filtered_df = lightduration_df[lightduration_df['Category'] == selected_category]

    # Create the bar chart
    fig = px.bar(
        filtered_df, 
        x='Month', 
        y='Hours', 
        title=f'Hours for {selected_category}')
    fig.update_traces(marker=dict(color='#314572'))
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the plot area
        paper_bgcolor='#f5f5f5'  # Light grey background for the whole chart
    )
    return dcc.Graph(id='graph1', figure=fig) 

# 折線圖氣溫回調
@app.callback(
    Output('tabs-content-2', 'children'),
    [Input('category-dropdown-line', 'value'),
     Input('graph-tabs', 'value')]
)
def update_temperature_line_chart(selected_category, tab):
    if tab != 'weather':
        return no_update
    # Filter the dataset for the selected category
    filtered_df = temperature_df[temperature_df['Category'] == selected_category]

    # Create the line chart
    fig = px.line(filtered_df, x='Month', y='Temperature', title=f'Temperature for {selected_category}', markers=True)
    fig.update_yaxes(rangemode='tozero')
    fig.update_layout(xaxis_title='Month', yaxis_title='Temperature (°C)')
    fig.update_traces(line=dict(color='#314572'))  # 設置折線顏色為藍色
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the plot area
        paper_bgcolor='#f5f5f5'  # Light grey background for the whole chart
    )
    return dcc.Graph(id='graph2', figure=fig)

# 折線圖日升日落回調
@app.callback(
    Output('tabs-content-4', 'children'),
    [Input('category-dropdown-line2', 'value'),
     Input('graph-tabs', 'value')]
)
def update_temperature_line_chart(selected_category, tab):
    if tab != 'weather':
        return no_update
    # Filter the dataset for the selected category
    filtered_df = suntime_df[suntime_df['Category'] == selected_category]

    # Create the line chart
    fig = px.line(filtered_df, x='Month', y='Time', title=f'Time for {selected_category}', markers=True)
    fig.update_yaxes(rangemode='tozero')
    fig.update_layout(xaxis_title='Month', yaxis_title='Time')
    fig.update_traces(line=dict(color='#314572'))  # 設置折線顏色為藍色
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the plot area
        paper_bgcolor='#f5f5f5'  # Light grey background for the whole chart
    )
    return dcc.Graph(id='graph2', figure=fig)

###千瑜景點部分
# Callback 根據選擇的地點更新圖片
# 若你使用 Dash 2.9+，可直接用 dash.ctx 取代 callback_context
from dash import callback_context  
from dash import html

@app.callback(
    [
        Output("location-dropdown", "value"),  # 更新下拉選單的選擇
        Output("image-container", "children"), # 更新下方區域顯示的圖片
        Output("geojson", "data")             # 更新地圖的 GeoJSON（包含樣式）資料
    ],
    [
        Input("geojson", "clickData"),        # 監聽地圖點擊事件
        Input("location-dropdown", "value")   # 監聽下拉式選單的改變
    ],
    State("geojson", "data")                  # 目前地圖的 GeoJSON 資料
)
def update_location_on_map_or_dropdown(map_click_data, dropdown_value, current_geojson):
    """
    說明：
    1. 同時支援地圖點擊 & 下拉選單的互動。
    2. 先判斷最後觸發 callback 的來源是地圖還是下拉選單。
    3. 若是地圖點擊，且有抓到 TOWNNAME，則使用該 TOWNNAME 更新下拉選單與圖片；
       如果點擊到的是空白處，就維持下拉選單當前的選擇。
    4. 若是下拉選單改變，則優先使用選單的值。
    5. 最後更新地圖的 highlight 樣式與下方圖片顯示。
    """

    # 1. 判斷誰是最後觸發 callback
    ctx = callback_context  # 如果是 Dash 2.9+ 可改用 dash.ctx
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # 2. 決定要用地圖帶進來的 town_name 還是下拉選單的值
    if triggered_id == "geojson":
        # 代表最後觸發的是地圖 clickData
        if map_click_data and "properties" in map_click_data:
            town_name = map_click_data["properties"].get("TOWNNAME", "")
        else:
            # 若點到空白處 or 取不到屬性, 則維持下拉選單原本的值
            town_name = dropdown_value  
    elif triggered_id == "location-dropdown":
        # 最後觸發的是下拉選單
        town_name = dropdown_value
    else:
        # 頁面初始化或其他狀況，預設維持下拉選單的值
        town_name = dropdown_value

    # 3. 找出該 town_name 在 locations 字典中對應的圖片資訊
    images = locations.get(town_name, [])

    # 4. 更新 GeoJSON 內每個 feature 的樣式，以高亮使用者選的 town_name
    for feature in current_geojson["features"]:
        if feature["properties"]["TOWNNAME"] == town_name:
            feature["properties"]["style"] = highlight_style
        else:
            feature["properties"]["style"] = default_style

    # 5. 生成圖片顯示區域
    image_elements = []
    for img in images:
        image_elements.append(
            html.Div([
                html.A(
                    html.Img(
                        src=f"/assets/{img['src']}",
                        style={
                            "width": "300px",
                            "height": "300px",
                            "margin": "10px",
                            "border": "2px solid #db9079",
                            "borderRadius": "10px"
                        }
                    ),
                    href=img["link"],   # 點擊圖片開地圖連結
                    target="_blank"
                ),
                html.Div(
                    html.A(
                        img["description"],
                        href=img["link"],
                        target="_blank",
                        style={
                            "marginTop": "5px",
                            "fontSize": "16px",
                            "color": "#333",
                            "textDecoration": "underline"
                        }
                    ),
                    style={"marginTop": "10px", "textAlign": "center"}
                )
            ], style={
                "display": "inline-block",
                "textAlign": "center",
                "margin": "10px",
                "width": "320px"
            })
        )

    # 6. 回傳：更新後的 dropdown value、圖片清單、與更新後的 geojson
    return town_name, image_elements, current_geojson




###千瑜美食部分
# Callback
@app.callback(
    [Output("graph-container", "children"),
     Output("image-container2", "children")],
    Input("data-dropdown", "value")
)
def update_content(selected_category):
    if selected_category == "food":
        df = data_food
        category = "food"
        title = "Top 5 Restaurants"
        x_label = "Count"
        y_label = "Restaurant"
    elif selected_category == "beverages":
        df = data_beverages
        category = "beverages"
        title = "Top 5 Beverages"
        x_label = "Count"
        y_label = "Beverage"
    else:
        selected_category == "snacks"
        df = data_snacks
        category = "snacks"
        title = "Top 5 Taiwanese Snacks"
        x_label = "Count"
        y_label = "Snack"

    # Create bar chart
    colors = pc.sample_colorscale("Blues", [i / len(df) for i in range(len(df))])
    fig = go.Figure(go.Bar(
        x=df["Count"],
        y=df[df.columns[0]],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=df["Count"],
        textposition="auto"
    ))

    fig.update_layout(
        title=title,
        title_x=0.5,
        template="plotly_white",
        margin=dict(l=20, r=50, t=50, b=50),
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='#f5f5f5'
    )

    graph = dcc.Graph(figure=fig, config={"displayModeBar": False})

    # Generate image links
    images = category_images.get(category, [])
    image_elements = [
        html.A(
            html.Div([
                html.Img(src=img["src"], style={"height": "200px", "margin": "10px", "border": "3px solid #deb522", "borderRadius": "15px"}),
                html.Div(img["description"], style={"marginTop": "5px", "fontSize": "16px", "color": "#314572"})
            ]),
            href=img["link"],
            target="_blank",
            style={"display": "inline-block", "width": "250px", "textAlign": "center"}
        ) for img in images
    ]

    return graph, image_elements

###學長建議部分
# 該月穿搭跟天氣回調
@app.callback(
    [Output("season-image", "children"),  
     Output("weather-info", "children")],  
    [Input("season-dropdown", "value")]  
)
def update_suggestions_and_weather(selected_month):
    # 月份對應
    month_to_number = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    # 月份對應季節
    month_to_season = {
        "Jan": "Winter", "Feb": "Winter", "Mar": "Spring",
        "Apr": "Spring", "May": "Spring", "Jun": "Summer",
        "Jul": "Summer", "Aug": "Summer", "Sep": "Autumn",
        "Oct": "Autumn", "Nov": "Autumn", "Dec": "Winter"
    }

    # 篩選氣溫及降雨
    selected_month_num = month_to_number[selected_month]
    selected_season = month_to_season.get(selected_month, "Unknown")

    # 氣溫及降雨資訊
    avg_temperature = temperature_df[temperature_df["Month"] == selected_month]["Temperature"].mean()
    avg_precipitation = precipitation_df[precipitation_df["Month"] == selected_month]["Precipitation"].mean()

    # 日出時間資訊
    sunrise_time_row =  suntime_df[( suntime_df["Category"] == "Sunrise Time") & ( suntime_df["Month"] == selected_month)]
    sunrise_time = None
    if not sunrise_time_row.empty:
        sunrise_time_value = sunrise_time_row["Time"].iloc[0]
        hours = int(sunrise_time_value)  # 取整數部分作為小時
        minutes = int((sunrise_time_value - hours) * 60)  # 小數部分轉為分鐘
        sunrise_time = f"{hours:02d}:{minutes:02d}"  # 格式化為 hh:mm

    # 日落時間資訊
    sunset_time_row =  suntime_df[( suntime_df["Category"] == "Sunset Time") & ( suntime_df["Month"] == selected_month)]
    sunset_time = None
    if not sunset_time_row.empty:
        sunset_time_value = sunset_time_row["Time"].iloc[0]
        hours = int(sunset_time_value)  # 取整數部分作為小時
        minutes = int((sunset_time_value - hours) * 60)  # 小數部分轉為分鐘
        sunset_time = f"{hours:02d}:{minutes:02d}"  # 格式化為 hh:mm
    
    # 日照時間資訊
    sun_time_row =  lightduration_df[( lightduration_df["Category"] == "Average Duration of Daylight") & ( lightduration_df["Month"] == selected_month)]
    sun_time = None
    if not sun_time_row.empty:
        sun_time_value = sun_time_row["Hours"].iloc[0]
        hours = int(sun_time_value)  # 取整數部分作為小時
        minutes = int((sun_time_value - hours) * 60)  # 小數部分轉為分鐘
        sun_time = f"{hours:02d}:{minutes:02d}"  # 格式化為 hh:mm

    # 左側天氣訊息
    weather_info = html.Div([
        html.H3(f"Weather in Taipei, {selected_month}", style={"color": "#314572", "textAlign": "left",'marginBottom': '10px',}),
        html.P(f"Average Temperature: {avg_temperature:.2f} °C" if not pd.isna(avg_temperature) else "Temperature data not available", style={"fontSize": "18px","color": "#314572"}),
        html.P(f"Average Precipitation: {avg_precipitation:.2f} mm" if not pd.isna(avg_precipitation) else "Precipitation data not available", style={"color": "#314572","fontSize": "18px"}),
        html.P(f"Sunrise Time: {sunrise_time}" if sunrise_time else "Sunrise time not available", style={"color": "#314572","fontSize": "18px"}),
        html.P(f"Sunset Time: {sunset_time}" if sunset_time else "Sunset time not available", style={"color": "#314572","fontSize": "18px"}),
        html.P(f"Duration of Daylight Time: {sun_time}" if sun_time else "Duration of Daylight Time not available", style={"color": "#314572","fontSize": "18px"})
    ])


    # 右側穿衣建議
    season_image = html.Div([
        html.H3(f"Season: {selected_season}", style={"textAlign": "center", "color": "#314572"}),
        html.Img(
            src=season_images[selected_season],
            style={"width": "300px", "height": "400px", "margin": "10px", "border": "3px solid #deb522", "borderRadius": "15px"}
        )
    ])

    return season_image, weather_info

# 行程推薦路徑連結回調

@app.callback(
    [Output("day_to_images", "children"),  
     Output("dynamic-link", "href")],
    Input("day-dropdown", "value")
)
def update_google_link(selected_day):
    # 根據天數篩選器的值生成不同的 Google 搜索連結和圖片
    if selected_day == "Cultural and Creative Itinerary":
        return (
            html.Div([
                html.H4("Cultural and Creative Itinerary"),
                html.P("Explore Taipei's creative culture and attractions."),
                html.Img(
                    src="assets/台灣文創.png",
                    style={"width": "100%", "border": "3px solid #deb522", "borderRadius": "15px"}
                )
            ]),
            "https://www.google.com/maps/dir/%E5%8F%B0%E5%8C%97%E8%BB%8A%E7%AB%99/100%E5%8F%B0%E5%8C%97%E5%B8%82%E4%B8%AD%E6%AD%A3%E5%8D%80%E5%85%AB%E5%BE%B7%E8%B7%AF%E4%B8%80%E6%AE%B51%E8%99%9F%E8%8F%AF%E5%B1%B11914%E6%96%87%E5%8C%96%E5%89%B5%E6%84%8F%E7%94%A2%E6%A5%AD%E5%9C%92%E5%8D%80/@25.0487963,121.5138317,15.21z/data=!4m16!4m15!1m5!1m1!1s0x3442a972a8266295:0xece39c57ea7e4e12!2m2!1d121.51375!2d25.04882!1m5!1m1!1s0x3442a96523e0246d:0xf1c9276707165c71!2m2!1d121.5293583!2d25.0440698!2m1!5e1!3e3?authuser=0&entry=ttu&g_ep=EgoyMDI1MDEwMS4wIKXMDSoASAFQAw%3D%3D"
        )
    elif selected_day == "Local Architectural Highlights Itinerary":
        return (
            html.Div([
                html.H4("Local Architectural Highlights Itinerary"),
                html.P("Discover Taipei's iconic architecture and landmarks."),
                html.Img(
                    src="assets/台灣建築.png", 
                    style={"width": "100%", "border": "3px solid #deb522", "borderRadius": "15px"}
                )
            ]),
            "https://www.google.com/maps/dir/%E5%8F%B0%E5%8C%97%E5%B8%82%E4%B8%AD%E6%AD%A3%E5%8D%80%E5%8F%B0%E5%8C%97%E8%BB%8A%E7%AB%99/%E5%8F%B0%E5%8C%97%E5%B8%82%E4%BF%A1%E7%BE%A9%E5%8D%80%E4%BF%A1%E7%BE%A9%E8%B7%AF%E4%BA%94%E6%AE%B5%E5%8F%B0%E5%8C%97101%E8%A7%80%E6%99%AF%E5%8F%B0/@25.0395297,121.5206476,14z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x3442a9727d969f51:0xd0f3033a81203ed2!2m2!1d121.5174062!2d25.0476133!1m5!1m1!1s0x3442abb6e9d93249:0xd508f7b3aa02d931!2m2!1d121.5648831!2d25.0336752!3e3?authuser=0&entry=ttu&g_ep=EgoyMDI1MDEwMS4wIKXMDSoASAFQAw%3D%3D"
        )
    elif selected_day == "Nature Itinerary":
        return (
            html.Div([
                html.H4("Nature Itinerary"),
                html.P("Enjoy Taipei's natural beauty and outdoor adventures."),
                html.Img(
                    src="assets/台灣溫泉.png",  # 另一張圖片 URL
                    style={"width": "100%", "border": "3px solid #deb522", "borderRadius": "15px"}
                )
            ]),
            "https://www.google.com/maps/dir/%E5%8F%B0%E5%8C%97%E5%B8%82%E4%B8%AD%E6%AD%A3%E5%8D%80%E5%8F%B0%E5%8C%97%E8%BB%8A%E7%AB%99/112%E5%8F%B0%E5%8C%97%E5%B8%82%E5%8C%97%E6%8A%95%E5%8D%80%E6%B9%96%E5%B1%B1%E8%B7%AF%E4%BA%8C%E6%AE%B5%E9%99%BD%E6%98%8E%E5%B1%B1%E5%9C%8B%E5%AE%B6%E5%85%AC%E5%9C%92%E9%99%BD%E6%98%8E%E5%B1%B1%E8%8A%B1%E9%90%98/@25.1037568,121.4423269,12z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x3442a972d969f51:0xd0f3033a81203ed2!2m2!1d121.5174062!2d25.0476133!1m5!1m1!1s0x3442b310336c2b39:0xde1b73b30eb78c9d!2m2!1d121.5390067!2d25.1590143!3e3?authuser=0&entry=ttu&g_ep=EgoyMDI1MDEwMS4wIKXMDSoASAFQAw%3D%3D"
        )
    else:
        return (
            html.Div(
                html.H4("Explore Taipei"),
                html.P("Find out more about Taipei and plan your trip."),
                )
            )



if __name__ == '__main__':
    app.run_server(debug=False)
