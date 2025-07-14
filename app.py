import streamlit as st
import os
import pandas as pd
from PIL import Image
import io
import base64
import random

# ========= CONFIG =========
IMAGE_DIR = "images"          # folder with survey images
CSV_PATH  = "ratings.csv"     # vote log
ACCENT    = "#FF6F61"         # coral highlight

# ========= PAGE SETUP & STYLE =========
st.set_page_config("APAKAH INI GAMBAR AI?", "🖼️", layout="wide")
st.markdown(f"""
    <style>
    :root {{ --accent: {ACCENT}; }}
    body {{ background:#f5f5f5; }}
    .stButton>button {{
        width:100%; height:3.5rem; font-size:1.6rem;
        background:var(--accent)!important; color:#fff!important;
        border:none!important; border-radius:.85rem!important;
    }}
    </style>
""", unsafe_allow_html=True)

# ========= HELPERS =========
@st.cache_resource
def list_images(folder: str):
    return sorted(f for f in os.listdir(folder)
                  if f.lower().endswith((".png", ".jpg", ".jpeg")))

@st.cache_resource
def load_image_bytes(path: str) -> bytes:
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def save_vote(user: str, pair_id: str, choice: str):
    df = pd.DataFrame([{"user": user, "pair": pair_id, "choice": choice}])
    mode   = "a" if os.path.exists(CSV_PATH) else "w"
    header = not os.path.exists(CSV_PATH)
    df.to_csv(CSV_PATH, mode=mode, header=header, index=False)

# ========= BUILD IMAGE PAIRS =========
all_imgs = list_images(IMAGE_DIR)
pairs = []
for fname in all_imgs:
    name, ext = os.path.splitext(fname)
    if name.endswith("_gt"):
        base = name[:-3]
        result_fname = f"{base}_result{ext}"
        if result_fname in all_imgs:
            pairs.append((base, fname, result_fname))
total = len(pairs)

# ========= SESSION STATE =========
if "idx" not in st.session_state:
    st.session_state.idx = 0

# ========= HEADER & EXPLAINER =========
st.markdown("<h1 style='text-align:center;color:var(--accent)'>🖼️ APAKAH INI GAMBAR AI?</h1>", unsafe_allow_html=True)
st.markdown("""
**Apa ini?**  
Sebuah **kuis singkat**: Anda akan melihat dua gambar. Satu dari gambar tersebut adalah gambar asli, dan satu lagi gambar hasil AI.  
Tugas Anda adalah pilih gambar yang menurut Anda **paling jernih**!

**Cara bermain:**  
1. Masukkan **Nama/ID** Anda.  
2. Amati dua gambar di sisi **Kiri** dan **Kanan**.  
3. Pilih mana yang menurut Anda **paling jernih**.  
4. Klik **➡️ Berikutnya** untuk melanjutkan.  
5. Ulangi hingga semua gambar selesai dinilai.
---  
""", unsafe_allow_html=True)

# ========= USER INPUT / DOWNLOAD GATE =========
user = st.text_input("Masukkan Nama / ID Anda:")
if not user:
    st.stop()

if user.strip().lower() == "download":
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        st.subheader("🗒️ Rekap Jawaban")
        st.dataframe(df)
        with open(CSV_PATH, "rb") as f:
            st.download_button(
                label="⬇️ Unduh Hasil Quiz (CSV)",
                data=f,
                file_name="ratings.csv",
                mime="text/csv"
            )
    else:
        st.error("Belum ada data untuk diunduh.")
    st.stop()

# ========= QUIZ LOOP =========
if st.session_state.idx < total:
    idx = st.session_state.idx
    base, gt_file, res_file = pairs[idx]
    st.markdown(f"**Pasangan {idx+1} dari {total}**")
    st.progress((idx + 1) / total)

    # prepare & shuffle
    items = [("Asli", gt_file), ("Hasil AI", res_file)]
    random.shuffle(items)
    (left_type, left_file), (right_type, right_file) = items

    # encode images
    left_b64  = base64.b64encode(load_image_bytes(os.path.join(IMAGE_DIR, left_file))).decode()
    right_b64 = base64.b64encode(load_image_bytes(os.path.join(IMAGE_DIR, right_file))).decode()

    # display side-by-side
    st.markdown(f"""
        <div style="display:flex; gap:1%;">
          <div style="flex:1; text-align:center;">
            <img src="data:image/png;base64,{left_b64}" style="width:100%; border-radius:0.5rem;"/>
            <p><strong>Kiri</strong></p>
          </div>
          <div style="flex:1; text-align:center;">
            <img src="data:image/png;base64,{right_b64}" style="width:100%; border-radius:0.5rem;"/>
            <p><strong>Kanan</strong></p>
          </div>
        </div>
    """, unsafe_allow_html=True)

    # choice form
    with st.form("quiz_form", clear_on_submit=True):
        choice = st.radio("Mana yang tampak paling jernih?", ["Kiri", "Kanan"], horizontal=True)
        if st.form_submit_button("➡️  Berikutnya"):
            picked = left_type if choice == "Kiri" else right_type
            save_vote(user, base, picked)
            st.session_state.idx += 1
            if hasattr(st, "rerun"):
                st.rerun()

# ========= COMPLETION =========
else:
    st.balloons()
    st.success("🎉 Selesai! Terima kasih atas partisipasi Anda.")
    if st.button("Mulai Ulang Quiz"):
        st.session_state.idx = 0
        if hasattr(st, "rerun"):
            st.rerun()
