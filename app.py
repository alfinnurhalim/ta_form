import streamlit as st
import os
import pandas as pd
from PIL import Image

# === CONFIG ===
IMAGE_DIR = "images"
CSV_PATH = "ratings.csv"
PRIMARY_COLOR = "#FF6F61"  # Coral accent
SECONDARY_COLOR = "#FFFFFF"

# === PAGE SETUP ===
st.set_page_config(
    page_title="Image Quality Survey",
    page_icon="🖼️",
    layout="wide"
)

# === CUSTOM STYLES ===
st.markdown(f"""
<style>
:root {{
    --primary-color: {PRIMARY_COLOR};
    --secondary-color: {SECONDARY_COLOR};
}}
body {{
    background-color: #f5f5f5;
}}
.css-card {{
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    max-width: 800px;
    margin: 2rem auto;
}}
.css-title {{
    font-size: 2.75rem;
    font-weight: 700;
    color: var(--primary-color);
    text-align: center;
    margin-bottom: 0.5rem;
}}
.css-subtitle {{
    font-size: 1.1rem;
    color: #555;
    text-align: center;
    margin-bottom: 1rem;
}}
.css-instruction {{
    font-size: 1rem;
    color: #333;
    margin-bottom: 1.5rem;
    line-height: 1.4;
}}
.css-slider > div[data-baseweb] {{
    width: 90% !important;
    margin: 0 auto;
}}
.css-next-button .stButton button {{
    background-color: var(--primary-color) !important;
    color: var(--secondary-color) !important;
    width: 100% !important;
    height: 4rem !important;
    font-size: 1.75rem !important;
    border-radius: 0.75rem !important;
    border: none !important;
}}
.css-download-button .stButton button {{
    background-color: var(--primary-color) !important;
    color: var(--secondary-color) !important;
    font-size: 1rem !important;
    border-radius: 0.5rem !important;
    border: none !important;
}}
</style>
""", unsafe_allow_html=True)

# === UTILS ===
@st.cache_data
def get_images(dir_path):
    return sorted([f for f in os.listdir(dir_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])

@st.cache_data
def load_img(path):
    return Image.open(path)

# Load image list
images = get_images(IMAGE_DIR)

# Initialize session state
if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.responses = []

# Main card
st.markdown("<div class='css-card'>", unsafe_allow_html=True)

# Header and Description
st.markdown("<div class='css-title'>🖼️ Survey Kualitas Gambar</div>", unsafe_allow_html=True)
st.markdown("<div class='css-subtitle'>Aplikasi ini menilai kejernihan gambar secara visual.</div>", unsafe_allow_html=True)

# Examples: Hazy vs Jernih
st.markdown("<div style='display:flex;justify-content:space-around;margin-bottom:1rem;'>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Contoh: Berkabut")
    st.image(load_img("/workspaces/ta_form/images/41_outdoor_input.jpg"), use_container_width=True)
with col2:
    st.subheader("Contoh: Jernih")
    st.image(load_img("/workspaces/ta_form/images/41_outdoor_gt.jpg"), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Instructions
st.markdown(
    "<div class='css-instruction'>"
    "Anda akan melihat beberapa gambar dengan tingkat kabut berbeda. "
    "Geser slider untuk menilai sejauh mana gambar tersebut jernih. "
    "Hasil Anda akan disimpan untuk analisis selanjutnya."
    "</div>", unsafe_allow_html=True
)

# User input and reset
def reset_survey():
    st.session_state.idx = 0
    st.session_state.responses = []

user = st.text_input("Masukkan Nama/ID Anda:")
if user:
    st.button("🔄 Reset Survey", on_click=reset_survey)

# Survey flow
if user:
    i = st.session_state.idx
    total = len(images)
    if i < total:
        # Progress
        st.markdown(f"**Gambar {i+1} dari {total} — Sisa {total-i-1}**")
        st.progress((i+1)/total)

        # Display current image
        img_path = os.path.join(IMAGE_DIR, images[i])
        img = load_img(img_path)
        st.image(img, use_container_width=True)

        # Slider and Next button (single click)
        st.markdown("<div style='width:80%;margin:1rem auto;'>", unsafe_allow_html=True)
        score = st.slider("Kejernihan:", 0, 100, 50, key=f"s_{i}")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button(f"➡️ Berikutnya ({i+1}/{total})"):
            st.session_state.responses.append({'user': user, 'score': score})
            st.session_state.idx += 1

    else:
        st.balloons()
        st.success("🎉 Semua gambar telah dinilai!")
        df = pd.DataFrame(st.session_state.responses)
        if os.path.exists(CSV_PATH):
            df = pd.concat([pd.read_csv(CSV_PATH), df], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Unduh Hasil", data=csv_bytes, file_name='ratings.csv', mime='text/csv')
else:
    st.warning("Silakan masukkan Nama/ID untuk memulai survei.")

st.markdown("</div>", unsafe_allow_html=True)
