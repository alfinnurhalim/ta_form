import streamlit as st
import os
import pandas as pd
from PIL import Image

# === CONFIG ===
IMAGE_DIR = "images"
CSV_PATH = "ratings.csv"
PRIMARY_COLOR = "#5B9BD5"  # Light blue

st.set_page_config(page_title="Image Quality Surveys", layout="wide")

# === STYLES ===
st.markdown(f"""
    <style>
        .big-score {{
            font-size: 72px;
            font-weight: bold;
            color: black;
            text-align: center;
        }}
        .score-label {{
            font-size: 20px;
            text-align: center;
            color: #444;
            margin-top: -10px;
        }}
        .slider-labels {{
            display: flex;
            justify-content: space-between;
            margin-top: -10px;
            font-weight: bold;
            color: #666;
            width: 400px;
            margin-left: auto;
            margin-right: auto;
        }}
        .image-title {{
            text-align: center;
            font-size: 22px;
            margin-bottom: 10px;
        }}
        .main-title {{
            text-align: center;
            font-size: 36px;
            color: {PRIMARY_COLOR};
            margin-bottom: 20px;
        }}
        .next-button-style button {{
            width: 100%;
            font-size: 28px;
            padding: 1.2em;
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: 10px;
        }}
    </style>
""", unsafe_allow_html=True)

# === APP TITLE ===
st.markdown("<div class='main-title'>🖼️ Image Quality Surveys</div>", unsafe_allow_html=True)

username = st.text_input("Enter your name or ID to begin:")

if username:
    st.write("---")
    ratings = []
    image_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    if 'index' not in st.session_state:
        st.session_state.index = 0
        st.session_state.responses = []

    total_images = len(image_files)
    current_index = st.session_state.index

    if current_index < total_images:
        img_file = image_files[current_index]
        img = Image.open(os.path.join(IMAGE_DIR, img_file))

        st.markdown(f"<div class='image-title'>Image {current_index + 1} of {total_images}</div>", unsafe_allow_html=True)
        col_img, col_score = st.columns([4, 1])

        with col_img:
            st.image(img, width=400)

        with col_score:
            st.markdown("<div class='score-label'>IMAGE<br>SCORE</div>", unsafe_allow_html=True)
            slider_val = st.slider("Seberapa jernih gambar ini?", 0, 100, 50, key=f"slider_{img_file}")
            st.markdown(f"<div class='big-score'>{slider_val}</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='slider-labels'>
            <span>Kabut</span>
            <span>Jernih</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='next-button-style'>", unsafe_allow_html=True)
        if st.button("➡️ Next Image"):
            st.session_state.responses.append([username, img_file, slider_val])
            st.session_state.index += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Final submission screen
        st.success("🎉 You have rated all images. Click below to submit.")
        if st.button("✅ Submit Ratings"):
            df = pd.DataFrame(st.session_state.responses, columns=["name", "image", "score"])
            if os.path.exists(CSV_PATH):
                old_df = pd.read_csv(CSV_PATH)
                df = pd.concat([old_df, df], ignore_index=True)
            df.to_csv(CSV_PATH, index=False)
            st.success("✅ Your ratings have been recorded. Thank you!")
            del st.session_state.index
            del st.session_state.responses
else:
    st.info("Please enter your name or ID to begin.")
