import streamlit as st
import os
import pandas as pd
from PIL import Image
from datetime import datetime

# === Config ===
IMAGE_DIR = "images"           # Folder containing question folders (e.g. images/image_01/)
CSV_PATH = "ratings.csv"        # Output file (appended, not overwritten)

# === App UI ===
st.title("Image Dehazing Quality Test")
st.write("Please rate the visual quality of each image set.")

# Get user info
name = st.text_input("Enter your name or ID")

if name:
    st.markdown("---")
    ratings = []

    # List image groups (each folder = 1 question)
    for idx, folder in enumerate(sorted(os.listdir(IMAGE_DIR))):
        folder_path = os.path.join(IMAGE_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        st.subheader(f"Question {idx + 1}: {folder}")
        image_files = sorted(os.listdir(folder_path))
        cols = st.columns(len(image_files))

        for i, img_name in enumerate(image_files):
            img_path = os.path.join(folder_path, img_name)
            with cols[i]:
                st.image(Image.open(img_path), caption=img_name, use_column_width=True)

        score = st.slider(
            f"Rate the visual quality for {folder}",
            min_value=1,
            max_value=5,
            value=3,
            key=f"slider_{folder}"
        )
        ratings.append([name, folder, score, datetime.now().isoformat()])
        st.markdown("---")

    if st.button("Submit Ratings"):
        df_new = pd.DataFrame(ratings, columns=["name", "image_group", "rating", "timestamp"])

        if os.path.exists(CSV_PATH):
            df_old = pd.read_csv(CSV_PATH)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_csv(CSV_PATH, index=False)
        st.success("Thank you! Your responses have been recorded.")
 
