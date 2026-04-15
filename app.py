import base64
import time
import streamlit as st
import streamlit.components.v1 as components
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, ThemeType
from supabase import create_client, Client
import random

# ==========================================
# 🔴 猎人请注意：填入你的 Supabase 密钥！
# ==========================================
SUPABASE_URL = "https://yqggxqllcutqatwjxmyx.supabase.co"
SUPABASE_KEY = "sb_publishable_66sM5garleFYSyoxfoBizg_WeoUpnAy"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# ==========================================
# 🧠 注入雷达记忆模块 (用于专属高亮)
# ==========================================
if 'last_coord' not in st.session_state:
    st.session_state['last_coord'] = None

# ==========================================
# 🦅 N109区专属离线坐标矩阵
# ==========================================
CITY_COORDS = {
    "临空市": (119.00, 32.00), "伦敦": (-0.12, 51.50), "纽约": (-74.00, 40.71),
    "东京": (139.69, 35.68), "巴黎": (2.35, 48.85), "首尔": (126.97, 37.56),
    "北京": (116.40, 39.90), "上海": (121.47, 31.23), "广州": (113.26, 23.12),
    "深圳": (114.05, 22.52), "成都": (104.06, 30.67), "重庆": (106.50, 29.53),
    "杭州": (120.15, 30.28), "武汉": (114.30, 30.59), "西安": (108.94, 34.26),
    "南京": (118.79, 32.04), "香港": (114.16, 22.28), "台北": (121.56, 25.03)
}

def get_coordinates(city_name):
    city_lower = city_name.strip().lower()
    if city_lower.endswith("市") and len(city_lower) > 1:
        city_lower = city_lower[:-1]
    if city_lower in CITY_COORDS:
        return CITY_COORDS[city_lower]
    return None, None

# ==========================================
# 🎨 N109区机车霓虹版 UI 深度定制
# ==========================================
st.set_page_config(page_title="N109区点亮计划", layout="wide", initial_sidebar_state="collapsed")

def set_bg_image(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(10, 5, 16, 0.8), rgba(10, 5, 16, 0.85)), url(data:image/jpeg;base64,{encoded_string}) !important;
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning("⚠️ 未检测到 bg.jpg，请确认背景图已放入文件夹，且名字是 bg.jpg！")

set_bg_image("bg.jpg")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+SC:wght@400;700&display=swap');
    html, body, [class*="css"] {font-family: 'Noto Sans SC', sans-serif;}
    h1, h2, h3 {font-family: 'Orbitron', 'Noto Sans SC', sans-serif !important; color: #ff004d !important; text-shadow: 0 0 15px rgba(255, 0, 77, 0.8); letter-spacing: 1px;}
    .stApp {background: linear-gradient(135deg, #050208 0%, #0a0510 50%, #1a050a 100%); color: #e0d8e0;}
    
    [data-baseweb="input"], [data-baseweb="input"] > div, [data-baseweb="input"] input,
    [data-baseweb="textarea"], [data-baseweb="textarea"] > div, [data-baseweb="textarea"] textarea {
        background-color: rgba(21, 10, 31, 0.8) !important;
        color: #ffb3c6 !important;
        -webkit-text-fill-color: #ffb3c6 !important; 
        border-color: #4a1525 !important;
    }
    [data-baseweb="input"] button {
        background-color: rgba(255, 0, 77, 0.1) !important;
        color: #ff004d !important;
    }
    
    [data-testid="stFormSubmitButton"] button, .stButton>button {
        background-color: rgba(20, 5, 15, 0.8) !important; 
        color: #ff004d !important; 
        border: 1px solid #ff004d !important; 
        box-shadow: 0 0 10px rgba(255, 0, 77, 0.3) inset, 0 0 10px rgba(255, 0, 77, 0.3) !important; 
        transition: all 0.3s ease-in-out !important; 
        font-weight: bold !important; 
        border-radius: 4px !important; 
        text-transform: uppercase !important; 
        letter-spacing: 2px !important;
    }
    [data-testid="stFormSubmitButton"] button:hover, .stButton>button:hover {
        background-color: #ff004d !important; 
        color: #ffffff !important; 
        box-shadow: 0 0 30px #ff004d, 0 0 10px #ffffff inset !important; 
        border-color: #ff004d !important; 
        transform: scale(1.02) !important;
    }
    
    .signal-card {background-color: rgba(21, 10, 31, 0.8); border-left: 4px solid #ff004d; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.5);}
    .signal-header {color: #c0f9ff; font-weight: bold; font-size: 1.1em; margin-bottom: 5px;} 
    .signal-city {color: #68aacd; font-size: 0.85em; margin-left: 10px;} 
    
    @keyframes signalBreathe {
        0% { opacity: 0.5; text-shadow: 0 0 2px rgba(224, 216, 224, 0.1); }
        50% { opacity: 1.0; text-shadow: 0 0 10px rgba(192, 249, 255, 0.4); } 
        100% { opacity: 0.5; text-shadow: 0 0 2px rgba(224, 216, 224, 0.1); }
    }
    @keyframes dotBlink {
        0% { opacity: 1; box-shadow: 0 0 10px #ff004d; }
        50% { opacity: 0.2; box-shadow: 0 0 2px #ff004d; }
        100% { opacity: 1; box-shadow: 0 0 10px #ff004d; }
    }
    
    .signal-msg {
        color: #e0d8e0; 
        font-size: 0.95em; 
        line-height: 1.4;
        animation: signalBreathe 4s infinite ease-in-out; 
    }
    .live-dot {
        display: inline-block; width: 12px; height: 12px; background-color: #ff004d; 
        border-radius: 50%; margin-right: 10px; margin-bottom: 2px;
        animation: dotBlink 1.5s infinite ease-in-out;
    }

    [data-testid="stAudio"] {
        background: linear-gradient(90deg, rgba(255, 0, 77, 0.15) 0%, rgba(21, 10, 31, 0.6) 50%, rgba(192, 249, 255, 0.15) 100%) !important;
        border: 1px solid rgba(255, 0, 77, 0.4) !important;
        border-radius: 8px !important;
        padding: 8px !important;
        box-shadow: 0 0 15px rgba(255, 0, 77, 0.2), inset 0 0 10px rgba(192, 249, 255, 0.1) !important;
        margin-bottom: 20px;
    }
    audio {color-scheme: dark !important; opacity: 0.85; outline: none;}
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .stTextInput label p, .stTextArea label p, .stNumberInput label p {
        color: #c0f9ff !important; 
        text-shadow: 0 0 8px rgba(192, 249, 255, 0.6) !important; 
        font-weight: bold !important;
        letter-spacing: 1px !important;
    }
    
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; text-align: center; }
        h3 { font-size: 1.3rem !important; text-align: center; }
        .stApp { background-attachment: scroll !important; } 
        [data-testid="stAudio"] { width: 100% !important; margin: 0 auto 20px auto !important; }
        .signal-card { padding: 10px; margin-bottom: 10px; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏍️ N109区点亮计划")

# 🦅 专属 BGM 播放器
try:
    with open("bgm.mp3", "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mpeg", loop=True)
    
    components.html(
        """
        <script>
            const setVolume = () => {
                const audios = window.parent.document.querySelectorAll('audio');
                audios.forEach(a => { a.volume = 0.5; });
            };
            setTimeout(setVolume, 100);
            setTimeout(setVolume, 500);
            setTimeout(setVolume, 1000);
        </script>
        """,
        height=0, width=0
    )
except Exception as e:
    st.warning(f"⚠️ BGM 加载失败: {e}")

def fetch_data():
    try:
        response = supabase.table("blessings").select("*").execute()
        data = response.data
        if data: data.reverse()
        return data
    except Exception as e:
        st.error(f"⚠️ 雷达读取失败: {e}")
        return []

def save_data(name, city, lon, lat, message):
    try:
        data = {"name": name, "city": city, "longitude": float(lon), "latitude": float(lat), "message": message}
        supabase.table("blessings").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"⚠️ 数据库写入失败: {e}")
        return False

# --- Pyecharts 赤红呼吸灯地图 (双层特效升级版) ---
def render_map(data_list):
    geo = (
        Geo(init_opts=opts.InitOpts(width="100%", height="500px", theme=ThemeType.DARK, bg_color="transparent"))
        .add_schema(
            maptype="world",
            itemstyle_opts=opts.ItemStyleOpts(area_color="#374260", border_color="#68aacd"),
            emphasis_itemstyle_opts=opts.ItemStyleOpts(area_color="#c0f9ff") 
        )
    )
    
    normal_pair = []
    highlight_pair = []
    last_coord = st.session_state.get('last_coord')

    if data_list:
        for i, item in enumerate(data_list):
            lon = item.get('longitude', 0)
            lat = item.get('latitude', 0)
            unique_city_id = f"{item.get('city', 'Unknown')}_{i}"
            geo.add_coordinate(unique_city_id, lon, lat)
            
            # 🦅 核心魔法：判断是不是刚刚发送的专属坐标
            if last_coord and abs(lon - last_coord[0]) < 0.0001 and abs(lat - last_coord[1]) < 0.0001:
                highlight_pair.append((unique_city_id, 1))
            else:
                normal_pair.append((unique_city_id, 1))
                
        # 第一层：普通猎人的暗红星团
        if normal_pair:
            geo.add("乌鸦芯片定位", normal_pair, type_=ChartType.EFFECT_SCATTER, symbol_size=8, color="#ff004d", effect_opts=opts.EffectOpts(is_show=True, brush_type="stroke", scale=3, period=2.5), label_opts=opts.LabelOpts(is_show=False))
        
        # 第二层：你的专属银白锁定 (超大涟漪)
        if highlight_pair:
            geo.add("🎯 专属锁定", highlight_pair, type_=ChartType.EFFECT_SCATTER, symbol_size=18, color="#C0C0C0", effect_opts=opts.EffectOpts(is_show=True, brush_type="stroke", scale=6, period=1.5), label_opts=opts.LabelOpts(is_show=False))
            
    geo.set_global_opts(title_opts=opts.TitleOpts(title="🎯 全球雷达响应", pos_left="center", title_textstyle_opts=opts.TextStyleOpts(color="#ff004d")))
    return geo.render_embed()

# --- 页面布局 ---
col1, col2 = st.columns([2, 1])
blessings_data = fetch_data()

with col1:
    st.markdown("### 🔴 为你闪烁的满城夜色")
    
    # 🦅 防线一：给手机端猎人的温馨提示
    st.markdown("<span style='color:#68aacd; font-size:0.85em;'>*📡 信号微弱时雷达可能隐匿。若未看到地图，请点击下方按钮重连。*</span>", unsafe_allow_html=True)
    
    # 🦅 防线二：赛博朋克风的强制重连按钮
    if st.button("🔄 重新扫描 N109 区雷达"):
        st.rerun()
        
    map_html = render_map(blessings_data)
    
    # 🦅 防线三：增加 iframe 高度，并关闭滚动条防止手机端滑动冲突
    components.html(map_html, height=550, scrolling=False)


with col2:
    st.markdown("### 📡 接入N109区频段")
    with st.form("blessing_form"):
        name = st.text_input("猎人代号")
        city = st.text_input("所在城市 (如: 上海, 伦敦, 纽约)")
        
        st.markdown("<span style='color:#885566; font-size:0.85em;'>*注：非省会城市无法定位，请手动输入经纬度*</span>", unsafe_allow_html=True)
        col_lon, col_lat = st.columns(2)
        with col_lon: manual_lon = st.number_input("备用经度", value=0.00, format="%.2f")
        with col_lat: manual_lat = st.number_input("备用纬度", value=0.00, format="%.2f")
            
        message = st.text_area("你想对秦彻说的话")
        submitted = st.form_submit_button("锁定并点亮坐标")
        
        if submitted:
            if SUPABASE_URL == "你的Project_URL":
                st.error("⚠️ 猎人！你忘记填 Supabase 密钥啦！")
            elif not name or not city:
                st.warning("⚠️ 代号和城市不能为空哦！")
            else:
                final_lon, final_lat = get_coordinates(city)
                if final_lon is None and final_lat is None:
                    if manual_lon != 0.00 or manual_lat != 0.00:
                        final_lon, final_lat = manual_lon, manual_lat
                
                if final_lon is not None and final_lat is not None:
                    jitter_lon = random.uniform(-0.05, 0.05)
                    jitter_lat = random.uniform(-0.05, 0.05)
                    final_lon += jitter_lon
                    final_lat += jitter_lat

                    success = save_data(name, city, final_lon, final_lat, message)
                    if success:
                        # 记录专属坐标
                        st.session_state['last_coord'] = (final_lon, final_lat)
                        
                        st.markdown(f"""
                        <div style="background: rgba(21, 10, 31, 0.8); border: 1px solid #c0f9ff; border-left: 4px solid #c0f9ff; padding: 15px; border-radius: 4px; box-shadow: 0 0 15px rgba(192, 249, 255, 0.2); margin-bottom: 15px;">
                            <span style="color: #c0f9ff; font-weight: bold; font-size: 1.1em;">🛰️ 信号接入成功！</span><br>
                            <span style="color: #e0d8e0; font-size: 0.95em;">猎人 <span style="color: #ff004d; font-weight: bold;">{name}</span>，坐标已锁定！雷达正在重启...</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 🦅 强制瞬间刷新网页，让银色高亮立刻出现！
                        time.sleep(1.5)
                        st.rerun()
                else:
                    st.error(f"❌ 乌鸦矩阵未收录【{city}】！请手动输入经纬度！")

# ==========================================
# 🦅 底部信号瀑布流展示区 (还原绝美三列排版)
# ==========================================
st.markdown("---")
st.markdown('### <span class="live-dot"></span>截获的猎人小姐信号 (实时)', unsafe_allow_html=True)

if blessings_data:
    display_data = blessings_data[:12] 
    cols = st.columns(3)
    for i, item in enumerate(display_data):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-header">
                    {item.get('name', '未知猎人')} 
                    <span class="signal-city">📍 {item.get('city', '未知坐标')}</span>
                </div>
                <div class="signal-msg">"{item.get('message', '发送了一段加密信号...')}"</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("<p style='color:#885566;'>当前频段安静，等待第一位猎人接入...</p>", unsafe_allow_html=True)
