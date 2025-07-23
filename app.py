import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import openrouteservice
import numpy as np

st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom right, #F3E9DC, #ffffff);
    }
    .stButton>button {
        background-color: #4A90E2 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        height: 3em !important;
        padding: 0.5em 1.5em !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button * {
        color: white !important;
    }
    .stButton>button:hover {
        background-color: #357ABD !important;
        color: white !important;
    }
    .nav-link {
        color: #4A90E2 !important;
        font-weight: 500 !important;
    }
    .nav-link.active {
        background-color: #4A90E2 !important;
        color: white !important;
        border-radius: 8px;
    }
    .css-1cypcdb, .css-1b7y2vv {
        background-color: #F3E9DC !important;
        border-radius: 10px;
        padding: 5px;
    }
    h1, h2, h3, h4, h5, h6, p, li, span, div {
        color: #4A4A4A !important;
    }
    .element-container .markdown-text-container {
        color: #4A4A4A !important;
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

# ==== Real Alexandria Locations Data ====
@st.cache_data
def load_data():
    routes = {
        "الخط الساحلي": [
            ("كوبري ستانلي", 31.23527506293558, 29.94862016099542),
            ("سان ستيفانو جراند بلازا", 31.24601782644359, 29.965841243803435),
            ("سيدي جابر", 31.2208617429026, 29.942250513945172),
            ("ميدان محطة الرمل", 31.203173647072855, 29.903093932160832),
            ("ميدان المنشية", 31.179140410012433, 29.93719286099709),
            ("مسجد المرسي أبو العباس", 31.205328252334947, 29.88281100517418),
            ("قلعة قايتباي", 31.213900540286925, 29.885381374489256)
        ],
        "خط وسط البلد": [
            ("جامعة الإسكندرية (الشاطبي)", 31.2107637709471, 29.913134876338436),
            ("دار الأوبرا", 31.19746482072032, 29.901693934010236),
            ("محطة مصر (السكة الحديد)", 31.193244662484144, 29.905219234852613),
            ("سوق العطارين", 31.198304814331237, 29.901702930311835),
            ("مكتبة الإسكندرية", 31.20895314416996, 29.909146329090756),
            ("متحف الأحياء المائية", 31.213294244949033, 29.885120607861804)
        ],
        "خط غرب الإسكندرية": [
            ("أبو قير", 31.312266479088542, 30.05994801374512),
            ("جامعة الإسكندرية (كلية الهندسة)", 31.206393797558594, 29.924822103325116),
            ("مستشفى الجلاء", 31.228963876594598, 29.995854303324382),
            ("سيتي سنتر الإسكندرية", 31.16679189991098, 29.93338827449065),
            ("مول مصر", 31.200286608755498, 29.9004150456541),
            ("برج العرب", 30.8453193910462, 29.582847132171086)
        ],
        "خط شرق الإسكندرية": [
            ("حديقة المنتزه", 31.285603998836688, 30.016782201194538),
            ("مستشفى المعمورة", 31.269708494525013, 30.0253957186656),
            ("ميدان أحمد عرابي (المكس)", 31.19899024396635, 29.893135287982894),
            ("العجمي", 31.09982701652395, 29.767096405349847),
            ("مطار برج العرب الدولي", 30.927699869281312, 29.700135287990776)
        ],
        "خط الورديان": [
            ("الورديان", 31.165292487511866, 29.865308151953784),
            ("باكوس", 31.239424797645636, 29.966830890491288),
            ("سيدي بشر", 31.25619309751545, 29.983371713222354),
            ("العصافرة", 31.20507762935945, 29.90655057633866),
            ("الإبراهيمية", 31.209006603155462, 29.933088160996242)
        ]
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
header_title = "🚐 Sekka plus - الإسكندرية" if lang == "ar" else "🚐 Sekka plus - Alexandria"
col1, col2, col3 = st.columns([1, 4, 1])

#  col1: title
with col1:
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; height: 100%;'>
            <h3 style='margin: 0; color:#2E7D32; font-size: 35px'>{header_title}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

#  col2: logo 
with col2:
    st.markdown(
        """
        <div style='text-align: center; margin-top: -120px; margin-bottom: -60px;'>
            <img src='https://i.postimg.cc/4NWxgM1v/logo.png' width='300' style='margin-bottom: 0px;'/>
        </div>
        """,
        unsafe_allow_html=True
    )

#  col3: change lang buttton 
with col3:
    st.markdown("<div style='height: 30px; margin-right: -40px'></div>", unsafe_allow_html=True)
    if st.button("English" if lang == "ar" else "العربية"):
        st.session_state["lang"] = "en" if lang == "ar" else "ar"
        st.rerun()

# ==== Menu ====
menu_options = {
    "ar": ["الرئيسية", "الخطوط", "خدمة مميزة", "عن التطبيق", "مساعدة", "ملاحظات"],
    "en": ["Home", "Routes", "Premium", "About", "Help", "Feedback"]
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
        folium.PolyLine(path, color='#4A90E2', weight=4).add_to(m)

    for _, row in route_data.iterrows():
        fare_text = f"{int(row['fare'])} ج" if row['fare'] == int(row['fare']) else f"{row['fare']} ج"
        popup = f"{row['stop_name']}<br>{'السعر' if lang == 'ar' else 'Fare'}: {fare_text}<br>{'الزمن' if lang == 'ar' else 'Time'}: {row['estimated_time_min']} دقيقة"
        folium.Marker([row['lat'], row['lon']], popup=popup, icon=folium.Icon(color='#F5A623')).add_to(m)

    st_folium(m, width=1500, height=550)

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
        folium.PolyLine(st.session_state["custom_path"], color='#4A90E2', weight=5).add_to(m2)
        folium.Marker([lat_start, lon_start], tooltip=start_name, icon=folium.Icon(color='blue')).add_to(m2)
        folium.Marker([lat_end, lon_end], tooltip=end_name, icon=folium.Icon(color='red')).add_to(m2)
        st_folium(m2, width=1500, height=500)

# ==== Premium Page ====
elif selected == menu_options[lang][2]:
    # Set language-specific texts
    if lang == "ar":
        title = "🎯 ميزة Premium: الوصول لمكان معين"
        subscribe_msg = "🔐 هذه الميزة متاحة فقط للمشتركين Premium."
        subscribe_btn = "اشترك في Premium (بـ 10 جنيه رمزي)"
        success_msg = "✅ تم تفعيل Premium."
        input_placeholder = "مثال: محطة مصر"
        input_label = "اكتب اسم المكان اللي رايح له ثم اضغط انتر"
        not_supported_msg = "⚠️ المكان غير مدعوم. جرب أحد هذه الأماكن:"
        result_title = "الطريق المقترح"
        board_from = "اركب من"
        get_off_at = "وانزل عند"
        cost = "التكلفة"
        estimated_time = "الوقت التقديري"
        currency = "جنيهاً"
        time_unit = "دقيقة"
    else:
        title = "🎯 Premium Feature: Reach a Specific Location"
        subscribe_msg = "🔐 This feature is only available for Premium subscribers."
        subscribe_btn = "Subscribe to Premium (10 EGP symbolic)"
        success_msg = "✅ Premium temporarily activated."
        input_placeholder = "Example: Misr Station"
        input_label = "Enter your destination and press Enter"
        not_supported_msg = "⚠️ Location not supported. Try one of these places:"
        result_title = "Suggested Route"
        board_from = "Board from"
        get_off_at = "Get off at"
        cost = "Cost"
        estimated_time = "Estimated time"
        currency = "EGP"
        time_unit = "minutes"

    st.markdown(f"### {title}")
   
    if not st.session_state["is_premium"]:
        st.markdown(subscribe_msg)
        if st.button(subscribe_btn):
            st.session_state["is_premium"] = True
            st.success(success_msg)
    else:
        # Add session variable to store selected start point
        if 'selected_start' not in st.session_state:
            st.session_state.selected_start = None
       
        destination = st.text_input(input_label,
                                 key="premium_destination",
                                 placeholder=input_placeholder,
                                 on_change=lambda: st.session_state.update(selected_start=None))
       
        # Bilingual landmarks dictionary
        alexandria_landmarks = {
    # Transportation
    "محطة مصر": (31.193244662484144, 29.905219234852613),
    "Misr Station": (31.193244662484144, 29.905219234852613),
    "ميدان محطة الرمل": (31.203173647072855, 29.903093932160832),
    "Raml Station Square": (31.203173647072855, 29.903093932160832),
   
    # Landmarks
    "مكتبة الإسكندرية": (31.20895314416996, 29.909146329090756),
    "Alexandria Library": (31.20895314416996, 29.909146329090756),
    "قلعة قايتباي": (31.213900540286925, 29.885381374489256),
    "Qaitbay Citadel": (31.213900540286925, 29.885381374489256),
    "مسجد المرسي أبو العباس": (31.205328252334947, 29.88281100517418),
    "Abu al-Abbas al-Mursi Mosque": (31.205328252334947, 29.88281100517418),
    "متحف الأحياء المائية": (31.213294244949033, 29.885120607861804),
    "Aquatic Museum": (31.213294244949033, 29.885120607861804),
   
    # Shopping
    "سيتي سنتر الإسكندرية": (31.16679189991098, 29.93338827449065),
    "City Centre Alexandria": (31.16679189991098, 29.93338827449065),
    "مول مصر": (31.200286608755498, 29.9004150456541),
    "Mall of Egypt": (31.200286608755498, 29.9004150456541),
    "سان ستيفانو جراند بلازا": (31.24601782644359, 29.965841243803435),
    "San Stefano Grand Plaza": (31.24601782644359, 29.965841243803435),
   
    # Education
    "جامعة الإسكندرية (الشاطبي)": (31.21077294696511, 29.913016859146865),
    "Alexandria University (Shatby)": (31.21077294696511, 29.913016859146865),
    "جامعة الإسكندرية (كلية الهندسة)": (31.206393797558594, 29.924822103325116),
    "Alexandria University (Engineering)": (31.206393797558594, 29.924822103325116),
   
    # Parks
    "حديقة المنتزه": (31.285603998836688, 30.016782201194538),
    "Montaza Park": (31.285603998836688, 30.016782201194538),
   
    # Transportation Hubs
    "مطار برج العرب الدولي": (30.927699869281312, 29.700135287990776),
    "Borg El Arab Airport": (30.927699869281312, 29.700135287990776),
    "كوبري ستانلي": (31.23527506293558, 29.94862016099542),
    "Stanley Bridge": (31.23527506293558, 29.94862016099542),
   
    # Hospitals
    "مستشفى الجلاء": (31.228963876594598, 29.995854303324382),
    "El Galaa Hospital": (31.228963876594598, 29.995854303324382),
    "مستشفى المعمورة": (31.269708494525013, 30.0253957186656),
    "El Maamoura Hospital": (31.269708494525013, 30.0253957186656),
   
    # Markets
    "سوق العطارين": (31.198304814331237, 29.901702930311835),
    "Attarine Market": (31.198304814331237, 29.901702930311835),
   
    # Squares
    "ميدان المنشية": (31.179140410012433, 29.93719286099709),
    "Mansheya Square": (31.179140410012433, 29.93719286099709),
    "ميدان أحمد عرابي (المكس)": (31.19899024396635, 29.893135287982894),
    "Ahmed Orabi Square (El Max)": (31.19899024396635, 29.893135287982894),
   
    # Neighborhoods
    "العجمي": (31.09982701652395, 29.767096405349847),
    "Agamy": (31.09982701652395, 29.767096405349847),
    "أبو قير": (31.312266479088542, 30.05994801374512),
    "Abu Qir": (31.312266479088542, 30.05994801374512),
    "الورديان": (31.165292487511866, 29.865308151953784),
    "Wardian": (31.165292487511866, 29.865308151953784),
    "سيدي جابر": (31.2208617429026, 29.942250513945172),
    "Sidi Gaber": (31.2208617429026, 29.942250513945172),
    "سيدي بشر": (31.25619309751545, 29.983371713222354),
    "Sidi Bishr": (31.25619309751545, 29.983371713222354),
    "العصافرة": (31.20507762935945, 29.90655057633866),
    "El Asafra": (31.20507762935945, 29.90655057633866),
    "الإبراهيمية": (31.209006603155462, 29.933088160996242),
    "Ibrahimia": (31.209006603155462, 29.933088160996242),
    "باكوس": (31.239424797645636, 29.966830890491288),
    "Bakos": (31.239424797645636, 29.966830890491288),
   
    # Cultural
    "دار الأوبرا": (31.19746482072032, 29.901693934010236),
    "Opera House": (31.19746482072032, 29.901693934010236)
        }
       
        if destination and destination in alexandria_landmarks:
            if st.session_state.selected_start is None:
                # Get random start point (excluding destination)
                possible_starts = [s for s in data['stop_name'].unique()
                                 if s != destination and not any(d in s for d in [destination, "محطة", "Station"])]
                if possible_starts:
                    st.session_state.selected_start = np.random.choice(possible_starts)
           
            if st.session_state.selected_start:
                start_row = data[data['stop_name'] == st.session_state.selected_start].iloc[0]
                dest_lat, dest_lon = alexandria_landmarks[destination]
               
                # Calculate route
                path = get_route_path(start_row['lat'], start_row['lon'], dest_lat, dest_lon)
               
                # Display results
                st.markdown(f"""
                <div style='border:1px solid #2E7D32; border-radius:10px; padding:15px; 10px 0; background-color:#f5f5f5;'>
                    <h4 style='color:#2E7D32;'>{result_title}</h4>
                    <p>{board_from} <strong>{st.session_state.selected_start}</strong></p>
                    <p>{get_off_at} <strong>{destination}</strong></p>
                    <hr style='8px 0;'>
                    <p>{cost}: <strong>{start_row['fare']} {currency}</strong></p>
                    <p>{estimated_time}: <strong>{start_row['estimated_time_min']} {time_unit}</strong></p>
                </div>
                """, unsafe_allow_html=True)
               
                # Show map
                m3 = folium.Map(location=[(start_row['lat'] + dest_lat)/2, (start_row['lon'] + dest_lon)/2],
                              zoom_start=13)
                folium.Marker([start_row['lat'], start_row['lon']],
                            tooltip=f"{board_from}: {st.session_state.selected_start}",
                            icon=folium.Icon(color='blue')).add_to(m3)
                folium.Marker([dest_lat, dest_lon],
                            tooltip=f"{get_off_at}: {destination}",
                            icon=folium.Icon(color='red')).add_to(m3)
                folium.PolyLine(path, color='purple', weight=4).add_to(m3)
                st_folium(m3, width=1500, height=500)
       
        elif destination and destination not in alexandria_landmarks:
            st.warning(not_supported_msg)
            # Show supported places in selected language
            if lang == "ar":
                supported_places = [place for place in alexandria_landmarks.keys() if not place.isascii()]
            else:
                supported_places = [place for place in alexandria_landmarks.keys() if place.isascii()]
            st.write(supported_places)

# ==== Routes Page ====
elif selected == menu_options[lang][1]:
    for route, df in data.groupby('route'):
        st.markdown(f"### 🚍 {route}")
        st.write(df[['stop_name', 'fare', 'estimated_time_min']])

# ==== About Page ====
elif selected == menu_options[lang][3]:
    st.markdown("### عن سكة بلس" if lang == "ar" else "### About sekka plus")
    team_list = ["أمير", "محمود", "يوسف", "عمار", "جاسر"] if lang == "ar" else ["Amir", "Mahmoud", "Youssef", "Ammar", "Jasser"]
    st.markdown("- " + "\n- ".join(team_list))

# ==== Help Page ====
elif selected == menu_options[lang][4]:
    st.markdown("### مساعدة" if lang == "ar" else "### Help")
    st.markdown("راسلنا على: support@whereismystop.com" if lang == "ar" else "Contact: support@whereismystop.com")

# ==== Feedback Page ====
elif selected == menu_options[lang][5]:  # index 5 = Feedback
    st.markdown("### 📝 ملاحظاتك تهمنا" if lang == "ar" else "### 📝 We value your feedback")

    email = st.text_input("بريدك الإلكتروني (اختياري)" if lang == "ar" else "Your email (optional)")

    rating = st.selectbox("اختر تقييمك 🌟", [1, 2, 3, 4, 5], index=4, format_func=lambda x: "⭐" * x)

    feedback = st.text_area("اكتب ملاحظتك هنا..." if lang == "ar" else "Write your feedback here...")

    if st.button("إرسال" if lang == "ar" else "Submit"):
        st.success("✅ شكراً لملاحظاتك!" if lang == "ar" else "✅ Thank you for your feedback!")


# ==== Footer ====
st.markdown("""
    <hr>
    <div style='text-align:center; color:#2E7D32; padding:10px;'>
        &copy; sekka plus — صنع بحب في إسكندرية 💙
    </div>
""", unsafe_allow_html=True)