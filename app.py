import streamlit as st
import os, random, io
import pandas as pd
from PIL import Image

# ========= CONFIG =========
IMAGE_DIR = "images"       # xxx_gt.*  +  xxx_result.*  pairs
CSV_PATH  = "ratings.csv"
ACCENT    = "#FF6F61"

# ========= PAGE & STYLE =========
st.set_page_config("Image Quality A/B Test", "🖼️", layout="wide")
st.markdown(
    f"""
    <style>
    :root {{ --accent:{ACCENT}; }}
    body {{ background:#f5f5f5; }}
    .stButton>button, .stForm div.stButton>button {{
        background:var(--accent)!important;color:#fff!important;
        border:none!important;border-radius:.75rem!important;
        height:3.2rem;font-size:1.25rem;
    }}
    </style>
    """, unsafe_allow_html=True
)

# ========= HELPERS =========
def list_pairs(folder: str):
    """Return list of dicts: [{'id','gt','res'}]"""
    gt, res = {}, {}
    for f in os.listdir(folder):
        name = f.lower()
        base = f.rsplit("_", 1)[0]
        if name.endswith(("_gt.jpg", "_gt.png", "_gt.jpeg")):
            gt[base]  = os.path.join(folder, f)
        elif name.endswith(("_result.jpg", "_result.png", "_result.jpeg")):
            res[base] = os.path.join(folder, f)
    return [{"id": k, "gt": gt[k], "res": res[k]} for k in gt if k in res]

@st.cache_resource
def load_bytes(path: str):
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def save_row(user, img_id, gt_side, choice_side):
    row = pd.DataFrame([{
        "user": user,
        "image_id": img_id,
        "gt_side": gt_side,      # 'left' / 'right'
        "choice": choice_side,   # 'left' / 'right'
        "is_gt_chosen": gt_side == choice_side
    }])
    exists = os.path.exists(CSV_PATH)
    row.to_csv(CSV_PATH, mode="a" if exists else "w",
               header=not exists, index=False)

# ========= DATA & SESSION =========
pairs = list_pairs(IMAGE_DIR)
total = len(pairs)
if "idx" not in st.session_state: st.session_state.idx = 0

# ========= UI HEADER =========
st.markdown(
    "<h1 style='text-align:center;color:var(--accent);margin-bottom:0'>🖼️ A/B Test Kejernihan Gambar</h1>",
    unsafe_allow_html=True
)

with st.expander("📋 Cara Mengisi"):
    st.markdown(
        """
1. Masukkan **Nama / ID** Anda.  
2. Klik gambar yang menurut Anda **lebih jernih**.  
3. Tekan **Next**. Posisi GT & hasil diacak.  
4. Ulangi hingga selesai — setiap respons dicatat otomatis.
        """
    )

# ========= USER =========
user = st.text_input("Masukkan Nama / ID Anda untuk memulai :")
if not user:
    st.stop()

# ========= SURVEY LOOP =========
if st.session_state.idx < total:
    i    = st.session_state.idx
    pair = pairs[i]

    # acak posisi GT-vs-result sekali per pasangan
    if "order" not in st.session_state or st.session_state.order_i != i:
        st.session_state.order_i       = i
        st.session_state.gt_left       = random.choice([True, False])

    gt_left = st.session_state.gt_left
    left_img, right_img = (pair["gt"], pair["res"]) if gt_left else (pair["res"], pair["gt"])

    st.markdown(f"**Gambar {i+1} dari {total}**")
    st.progress((i+1)/total)

    # clickable images
    selection = st.image_select(
        "Klik gambar yang LEBIH JERNIH:",
        [load_bytes(left_img), load_bytes(right_img)],
        captions=["Kiri", "Kanan"],
        use_container_width=True,
        return_index=True          # need Streamlit ≥ 1.29
    )

    # Next button
    if st.button("➡️ Next", disabled=(selection is None)):
        choice_side = "left" if selection == 0 else "right"
        save_row(user, pair["id"], "left" if gt_left else "right", choice_side)
        st.session_state.idx += 1
        st.rerun()

# ========= FINISH =========
else:
    st.balloons()
    st.success("🎉 Selesai! Terima kasih atas partisipasinya.")
    if st.button("Mulai Ulang"):
        st.session_state.idx = 0
        st.rerun()
