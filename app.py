import streamlit as st
import os
import pandas as pd
from PIL import Image
import io

# ========= CONFIG =========
IMAGE_DIR = "images"          # folder with survey images
CSV_PATH  = "ratings.csv"     # vote log
ACCENT    = "#FF6F61"         # coral highlight

# ========= PAGE & STYLE =========
st.set_page_config("Image Quality Survey", "🖼️", layout="wide")
st.markdown(
    f"""
    <style>
    :root {{ --accent: {ACCENT}; }}
    body {{ background:#f5f5f5; }}
    .stButton>button {{
        width:100%;height:3.5rem;font-size:1.6rem;
        background:var(--accent)!important;color:#fff!important;
        border:none!important;border-radius:.85rem!important;
    }}
    .slider-wrap div[data-baseweb]{{ width:100%!important;margin:0; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ========= HELPERS =========
@st.cache_resource
def list_images(folder: str):
    """Return sorted list of image filenames."""
    return sorted(
        f for f in os.listdir(folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )

@st.cache_resource
def load_image_bytes(path: str) -> bytes:
    """Read image once, keep in memory as PNG bytes for fast reuse."""
    img = Image.open(path).convert("RGB")  # originals already small
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def save_vote(user: str, fname: str, score: int):
    row = pd.DataFrame([{"user": user, "image": fname, "score": score}])
    mode   = "a" if os.path.exists(CSV_PATH) else "w"
    header = not os.path.exists(CSV_PATH)
    row.to_csv(CSV_PATH, mode=mode, header=header, index=False)

# ========= DATA & SESSION =========
images = list_images(IMAGE_DIR)
total  = len(images)
if "idx" not in st.session_state:
    st.session_state.idx = 0

# ========= UI =========
st.markdown(
    "<h1 style='text-align:center;color:var(--accent);margin-bottom:0'>🖼️ Survey Kualitas Gambar</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;margin-top:0'>Nilai seberapa jernih setiap gambar.</p>",
    unsafe_allow_html=True,
)

# example pair
col_hazy, col_clear = st.columns(2)
with col_hazy:
    st.subheader("Contoh Berkabut")
    st.image(load_image_bytes(os.path.join(IMAGE_DIR, "41_outdoor_input.jpg")),
             use_container_width=True)
with col_clear:
    st.subheader("Contoh Jernih")
    st.image(load_image_bytes(os.path.join(IMAGE_DIR, "41_outdoor_gt.jpg")),
             use_container_width=True)
st.markdown("---")

# user id
user = st.text_input("Masukkan Nama / ID Anda untuk memulai :")
if not user:
    st.stop()    # wait for ID

# survey loop
if st.session_state.idx < total:
    i = st.session_state.idx
    st.markdown(f"**Gambar {i+1} dari {total} — sisa {total-i-1}**")
    st.progress((i + 1) / total)

    st.image(load_image_bytes(os.path.join(IMAGE_DIR, images[i])),
             use_container_width=True)

    with st.form("rating_form", clear_on_submit=True):
        st.markdown("<div class='slider-wrap'>", unsafe_allow_html=True)
        score = st.slider("0 = Kabut Pekat | 100 = Sangat Jernih", 0, 100, 50,
                          key=f"s_{i}")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.form_submit_button("➡️  Berikutnya"):
            save_vote(user, images[i], score)
            st.session_state.idx += 1
            if hasattr(st, "rerun"): st.rerun()  # Streamlit ≥1.30
else:
    st.balloons()
    st.success("🎉 Semua gambar telah dinilai! Terima kasih.")
    if st.button("Mulai Ulang"):
        st.session_state.idx = 0
        if hasattr(st, "rerun"): st.rerun()
