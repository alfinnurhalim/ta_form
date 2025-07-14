import streamlit as st
import os, random, io, base64
import pandas as pd
from PIL import Image

# ========= CONFIG =========
TITLE     = "Test Kejernihan Gambar"
IMAGE_DIR = "images"           # *_gt.* and *_result.* pairs
CSV_PATH  = "ratings.csv"
ACCENT    = "#FF6F61"

# ========= PAGE & GLOBAL STYLE =========
st.set_page_config(TITLE, "🖼️", layout="wide")
st.markdown(
    f"""
    <style>
    :root {{ --accent:{ACCENT}; }}
    body {{ background:#f5f5f5; }}
    .stButton>button, .stForm div.stButton>button {{
        background:var(--accent)!important;color:#fff!important;
        border:none!important;border-radius:.7rem!important;
        height:3.1rem;font-size:1.2rem;
    }}
    /* Flex wrapper keeps images side-by-side on phones */
    .pair-wrapper {{
        display:flex;justify-content:space-between;align-items:center;
        gap:6px;margin-bottom:.3rem;
    }}
    .pair-wrapper img {{
        width:48vw;max-width:360px;height:auto;border-radius:.5rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ========= HELPERS =========
def list_pairs(folder: str):
    gt, res = {}, {}
    for f in os.listdir(folder):
        fname = f.lower()
        base  = f.rsplit("_", 1)[0]          # before _gt / _result
        if fname.endswith(("_gt.jpg", "_gt.png", "_gt.jpeg")):
            gt[base] = os.path.join(folder, f)
        elif fname.endswith(("_result.jpg", "_result.png", "_result.jpeg")):
            res[base] = os.path.join(folder, f)
    return [
        {"id": k, "gt": gt[k], "res": res[k]}
        for k in gt if k in res
    ]

@st.cache_resource
def load_b64(path: str) -> str:
    """Return base64-encoded PNG (small images)."""
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

def save_row(user, img_id, gt_side, choice):
    row = pd.DataFrame([{
        "user": user,
        "image_id": img_id,
        "gt_side": gt_side,          # left / right
        "choice": choice,            # left / right
        "is_gt_chosen": gt_side == choice
    }])
    exists = os.path.exists(CSV_PATH)
    row.to_csv(CSV_PATH, mode="a" if exists else "w",
               header=not exists, index=False)

# ========= DATA & SESSION =========
pairs = list_pairs(IMAGE_DIR)
total = len(pairs)
if "idx" not in st.session_state: st.session_state.idx = 0  # current index

# ========= HEADER =========
st.markdown(
    f"<h1 style='text-align:center;color:var(--accent);margin-bottom:0'>{TITLE}</h1>",
    unsafe_allow_html=True
)

with st.expander("📋 Cara Mengisi"):
    st.markdown(
        """
1. Masukkan **Nama / ID** Anda.  
2. Untuk setiap pasangan, klik radio **Kiri** atau **Kanan** sesuai gambar yang **lebih jernih**.  
   Posisi ground-truth dan hasil **diacak**.  
3. Tekan **Next** untuk merekam jawaban.  
4. Ulangi hingga selesai — setiap respons direkam otomatis.
        """
    )

# ========= USER ID =========
user = st.text_input("Masukkan Nama / ID Anda:")
if not user:
    st.stop()

# ========= SURVEY LOOP =========
if st.session_state.idx < total:
    i    = st.session_state.idx
    pair = pairs[i]

    # random order once per pair
    if "order_idx" not in st.session_state or st.session_state.order_idx != i:
        st.session_state.order_idx = i
        st.session_state.gt_left   = random.choice([True, False])

    gt_left = st.session_state.gt_left
    left_b64  = load_b64(pair["gt"] if gt_left else pair["res"])
    right_b64 = load_b64(pair["res"] if gt_left else pair["gt"])

    st.markdown(f"**Gambar {i+1} dari {total}**")
    st.progress((i + 1) / total)

    # ---- Side-by-side images (always horizontal) ----
    st.markdown(
        f"""
        <div class="pair-wrapper">
            <img src="data:image/png;base64,{left_b64}">
            <img src="data:image/png;base64,{right_b64}">
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---- Choice form ----
    with st.form("choice_form", clear_on_submit=True):
        choice_label = st.radio(
            "Pilih gambar yang LEBIH JERNIH:",
            ["Kiri", "Kanan"],
            horizontal=True,
            key=f"choice_{i}"
        )
        submitted = st.form_submit_button("➡️ Next")
        if submitted:
            choice_side = "left" if choice_label == "Kiri" else "right"
            save_row(user, pair["id"],
                     "left" if gt_left else "right",
                     choice_side)
            st.session_state.idx += 1
            if hasattr(st, "rerun"): st.rerun()
else:
    st.balloons()
    st.success("🎉 Survey selesai! Terima kasih atas partisipasinya.")
    if st.button("Mulai Ulang"):
        st.session_state.idx = 0
        if hasattr(st, "rerun"): st.rerun()
