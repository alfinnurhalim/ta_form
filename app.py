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

# ========= PAGE & STYLE =========
st.set_page_config("Blind Clarity Quiz", "🖼️", layout="wide")
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
    return sorted(f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg")))

@st.cache_resource
def load_image_bytes(path: str) -> bytes:
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def save_vote(user: str, pair_id: str, choice_label: str):
    """Append response: which label user picked (GT or Rekonstruksi)."""
    df = pd.DataFrame([{
        "user": user,
        "pair": pair_id,
        "choice": choice_label
    }])
    mode   = "a" if os.path.exists(CSV_PATH) else "w"
    header = not os.path.exists(CSV_PATH)
    df.to_csv(CSV_PATH, mode=mode, header=header, index=False)

# ========= BUILD PAIRS =========
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

# ========= SESSION =========
if "idx" not in st.session_state:
    st.session_state.idx = 0

# ========= HEADER & EXPLAINER =========
st.markdown("<h1 style='text-align:center;color:var(--accent)'>🖼️ Blind Clarity Quiz</h1>", unsafe_allow_html=True)
st.markdown("""
**Apa ini?**  
Sebuah **QUIZ**: antara dua gambar—satu _Ground Truth_ (GT) asli, dan satu _AI-reconstructed_ (hasil)—mana yang benar-benar gambar nyata?  
Gambar-gambar ini awalnya digunakan untuk **image dehazing**; satu sisi adalah GT, satu lagi hasil rekonstruksi AI.  
Tujuan: lihat apakah AI dapat “menipu” mata manusia.

**Cara main:**  
1. Masukkan **Nama/ID** Anda.  
2. Untuk setiap pasangan, perhatikan dua gambar di sisi **Kiri** dan **Kanan** (urutan acak).  
3. Pilih mana yang menurut Anda **GT (nyata)** atau **Rekonstruksi (AI)**.  
4. Klik **➡️ Berikutnya** untuk menyimpan jawaban dan lanjut quiz.  
5. Ulangi hingga semua pasangan terjawab.
---
""", unsafe_allow_html=True)

# ========= USER ID =========
user = st.text_input("Masukkan Nama / ID Anda untuk memulai:")
if not user:
    st.stop()

# ========= QUIZ LOOP =========
if st.session_state.idx < total:
    idx = st.session_state.idx
    base, gt_file, res_file = pairs[idx]
    st.markdown(f"**Pasangan {idx+1} dari {total}**")
    st.progress((idx + 1) / total)

    # assemble and shuffle
    items = [("GT", gt_file), ("Rekonstruksi", res_file)]
    random.shuffle(items)
    left_label,  left_file  = items[0]
    right_label, right_file = items[1]

    # load images
    left_b64  = base64.b64encode(load_image_bytes(os.path.join(IMAGE_DIR, left_file))).decode()
    right_b64 = base64.b64encode(load_image_bytes(os.path.join(IMAGE_DIR, right_file))).decode()

    # display side-by-side
    st.markdown(f"""
    <div style="display:flex; flex-wrap:nowrap; gap:1%;">
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
        choice = st.radio("Mana yang GT (nyata)?", ["Kiri", "Kanan"], horizontal=True)
        if st.form_submit_button("➡️  Berikutnya"):
            picked = left_label  if choice == "Kiri" else right_label
            save_vote(user, base, picked)
            st.session_state.idx += 1
            if hasattr(st, "rerun"):
                st.rerun()

# ========= FINISH =========
else:
    st.balloons()
    st.success("🎉 Selesai! Terima kasih atas partisipasi Anda.")
    if st.button("Mulai Ulang Quiz"):
        st.session_state.idx = 0
        if hasattr(st, "rerun"):
            st.rerun()
