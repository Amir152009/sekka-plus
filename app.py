import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import openrouteservice
import numpy as np

# ==== CSS للتصميم الأخضر الكامل ====
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom right, #e8f5e9, #ffffff);
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
    }
    .nav-link {
        color: #2E7D32 !important;
        font-weight: 500 !important;
    }
    .nav-link.active {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 8px;
    }
    .css-1cypcdb, .css-1b7y2vv {
        background-color: #e8f5e9 !important;
        border-radius: 10px;
        padding: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==== ORS API ====
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijk4NmY4MmU4MGNhMzRjY2VhMmZlODdiNTkyZTRkNjA2IiwiaCI6Im11cm11cjY0In0="
client = openrouteservice.Client(key=ORS_API_KEY)

# ==== language & premium ====
if "lang" not in st.session_state:
    st.session_state["lang"] = "ar"
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False
lang = st.session_state["lang"]

# ==== data ====
@st.cache_data
def load_data():
    routes = {
        "route 1": [
            ("محطة الرمل", 31.2001, 29.9187),
            ("سيدي جابر", 31.2231, 29.9489),
            ("كليوباترا", 31.2256, 29.9634),
            ("زيزينيا", 31.2341, 29.9721),
            ("فيكتوريا", 31.247759, 29.978621)
        ],
        "route 2": [
            ("المنشية", 31.1962, 29.8957),
            ("بحري", 31.2005, 29.8837),
            ("الجمرك", 31.2031, 29.8720),
        ],
    }
    dfs = []
    for route_name, stops in routes.items():
        df = pd.DataFrame(stops, columns=["stop_name", "lat", "lon"])
        df["route"] = route_name
        df = add_fare_and_time(df)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def add_fare_and_time(df):
    df = df.copy()
    base_fare = np.random.choice([4, 4.5, 5, 5.5, 6])
    base_time = np.random.uniform(1.5, 2.5)
    fares = [base_fare]
    times = [round(base_time, 1)]
    for _ in range(1, len(df)):
        fare = np.random.choice([4, 4.5, 5, 5.5, 6])
        time = round(base_time + np.random.uniform(1, 3), 1)
        fares.append(fare)
        times.append(time)
    df["fare"] = fares
    df["estimated_time_min"] = times
    return df

data = load_data()

@st.cache_data(show_spinner=False)
def get_route_path(lat1, lon1, lat2, lon2):
    coords = ((lon1, lat1), (lon2, lat2))
    try:
        route = client.directions(coords, profile='driving-car', format='geojson')
        geometry = route['features'][0]['geometry']['coordinates']
        return [(lat, lon) for lon, lat in geometry]
    except:
        return [(lat1, lon1), (lat2, lon2)]

if "custom_path" not in st.session_state:
    st.session_state["custom_path"] = None
    st.session_state["custom_start"] = None
    st.session_state["custom_end"] = None

# ==== header ====
header_title = "🚐 Where is My Stop? - الإسكندرية" if lang == "ar" else "🚐 Where is My Stop? - Alexandria"
col1, col2 = st.columns([8, 2])
with col1:
    st.markdown(f"<h2 style='color:#2E7D32;'>{header_title}</h2>", unsafe_allow_html=True)
with col2:
    if st.button("English" if lang == "ar" else "العربية"):
        st.session_state["lang"] = "en" if lang == "ar" else "ar"
        st.rerun()

# ==== Menu ====
menu_options = {
    "ar": ["الرئيسية", "الخطوط", "خدمة مميزة", "عن التطبيق", "مساعدة"],
    "en": ["Home", "Routes", "Premium", "About", "Help"]
}
icons = ["house", "list-task", "star", "info-circle", "question-circle"]
selected = option_menu(menu_title=None, options=menu_options[lang], icons=icons, orientation="horizontal")

# ==== Main Page ====
if selected == menu_options[lang][0]:
    st.markdown("### اختر خط الميكروباص" if lang == "ar" else "### Select a Microbus Route")
    route = st.selectbox("اختر خط:" if lang == "ar" else "Choose Route:", data['route'].unique())
    route_data = data[data['route'] == route]
    m = folium.Map(location=[31.2156, 29.9553], zoom_start=13)

    coords = route_data[['lat', 'lon']].values.tolist()
    for i in range(len(coords)-1):
        lat1, lon1 = coords[i]
        lat2, lon2 = coords[i+1]
        path = get_route_path(lat1, lon1, lat2, lon2)
        folium.PolyLine(path, color='green', weight=4).add_to(m)

    for _, row in route_data.iterrows():
        fare_text = f"{int(row['fare'])} ج" if row['fare'] == int(row['fare']) else f"{row['fare']} ج"
        popup = f"{row['stop_name']}<br>{'السعر' if lang == 'ar' else 'Fare'}: {fare_text}<br>{'الزمن' if lang == 'ar' else 'Time'}: {row['estimated_time_min']} دقيقة"
        folium.Marker([row['lat'], row['lon']], popup=popup, icon=folium.Icon(color='darkgreen')).add_to(m)

    st_folium(m, width=1000, height=550)

    st.markdown("### ابحث عن طريق بين محطتين" if lang == "ar" else "### Find Route Between Two Stops")
    stop_names = route_data['stop_name'].tolist()
    start_stop = st.selectbox("من المحطة:" if lang == "ar" else "From Stop:", stop_names)
    end_stop = st.selectbox("إلى المحطة:" if lang == "ar" else "To Stop:", stop_names[::-1])

    if st.button("اعرض الطريق" if lang == "ar" else "Show Route"):
        start_row = route_data[route_data['stop_name'] == start_stop].iloc[0]
        end_row = route_data[route_data['stop_name'] == end_stop].iloc[0]
        path = get_route_path(start_row['lat'], start_row['lon'], end_row['lat'], end_row['lon'])
        st.session_state["custom_path"] = path
        st.session_state["custom_start"] = (start_row['lat'], start_row['lon'], start_stop)
        st.session_state["custom_end"] = (end_row['lat'], end_row['lon'], end_stop)

    if st.session_state["custom_path"]:
        lat_start, lon_start, start_name = st.session_state["custom_start"]
        lat_end, lon_end, end_name = st.session_state["custom_end"]
        m2 = folium.Map(location=[(lat_start + lat_end) / 2, (lon_start + lon_end) / 2], zoom_start=13)
        folium.PolyLine(st.session_state["custom_path"], color='red', weight=5).add_to(m2)
        folium.Marker([lat_start, lon_start], tooltip=start_name, icon=folium.Icon(color='blue')).add_to(m2)
        folium.Marker([lat_end, lon_end], tooltip=end_name, icon=folium.Icon(color='red')).add_to(m2)
        st_folium(m2, width=1000, height=500)

# ==== Premium Page ====
elif selected == menu_options[lang][2]:
    st.markdown("### 🎯 ميزة Premium: الوصول لمكان معين")
    if not st.session_state["is_premium"]:
        st.markdown("🔐 هذه الميزة متاحة فقط للمشتركين Premium.")
        if st.button("اشترك في Premium (بـ 10 جنيه رمزي)"):
            st.session_state["is_premium"] = True
            st.success("✅ تم تفعيل Premium مؤقتًا لتجربة النموذج.")
    else:
        destination = st.text_input("اكتب اسم المكان اللي رايح له (مثلاً: محطة مصر)")
        if destination:
            fake_places = {
                "محطة مصر": (31.1910, 29.9020),
                "مكتبة الإسكندرية": (31.2089, 29.9092),
                "ستانلي": (31.2405, 29.9633),
            }
            if destination in fake_places:
                dest_lat, dest_lon = fake_places[destination]
                dists = data.apply(lambda row: np.sqrt((row['lat'] - dest_lat)**2 + (row['lon'] - dest_lon)**2), axis=1)
                nearest_row = data.loc[dists.idxmin()]
                path = get_route_path(nearest_row['lat'], nearest_row['lon'], dest_lat, dest_lon)
                m3 = folium.Map(location=[(nearest_row['lat'] + dest_lat)/2, (nearest_row['lon'] + dest_lon)/2], zoom_start=13)
                folium.Marker([nearest_row['lat'], nearest_row['lon']], tooltip=f"اركب من: {nearest_row['stop_name']}", icon=folium.Icon(color='blue')).add_to(m3)
                folium.Marker([dest_lat, dest_lon], tooltip=f"انزل عند: {destination}", icon=folium.Icon(color='red')).add_to(m3)
                folium.PolyLine(path, color='purple', weight=4).add_to(m3)
                st_folium(m3, width=1000, height=500)
                st.markdown(f"🚌 اركب من **{nearest_row['stop_name']}** وانزل عند **{destination}**")
                st.markdown(f"💰 التكلفة: **{nearest_row['fare']} ج**")
                st.markdown(f"⏱️ الوقت التقديري: **{nearest_row['estimated_time_min']} دقيقة**")
            else:
                st.warning("⚠️ المكان غير مدعوم حاليًا في النموذج التجريبي.")

# ==== Routes Page ====
elif selected == menu_options[lang][1]:
    for route, df in data.groupby('route'):
        st.markdown(f"### 🚍 {route}")
        st.write(df[['stop_name', 'fare', 'estimated_time_min']])

# ==== About Page ====
elif selected == menu_options[lang][3]:
    st.markdown("### عن Where is My Stop؟" if lang == "ar" else "### About Where is My Stop?")
    team_list = ["عمار", "أمير", "يوسف", "محمود", "جاسر"] if lang == "ar" else ["Ammar", "Amir", "Youssef", "Mahmoud", "Jasser"]
    st.markdown("- " + "\n- ".join(team_list))

# ==== Help Page ====
elif selected == menu_options[lang][4]:
    st.markdown("### مساعدة" if lang == "ar" else "### Help")
    st.markdown("راسلنا على: support@whereismystop.com" if lang == "ar" else "Contact: support@whereismystop.com")

# ==== Footer ====
st.markdown("""
    <hr>
    <div style='text-align:center; color:#2E7D32; padding:10px;'>
        &copy; 2025 Where is My Stop? — صنع بحب في إسكندرية 💚
    </div>
""", unsafe_allow_html=True)