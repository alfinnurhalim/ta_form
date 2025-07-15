import streamlit as st
import os
import pandas as pd
from PIL import Image
import io
import base64
import random

# ========= CONFIG =========
IMAGE_DIR = "images"
CSV_PATH = "ratings.csv"
ACCENT = "#FF6F61"

# ========= PAGE SETUP =========
st.set_page_config("YANG MANA YANG AI", "🖼️", layout="wide")
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

def save_vote(user: str, pair_id: str, choice_label: str):
    choice_val = 1 if choice_label.lower() == "asli" else 0  # 1 = GT, 0 = AI
    df = pd.DataFrame([{"user": user, "pair": pair_id, "choice": choice_val}])
    mode = "a" if os.path.exists(CSV_PATH) else "w"
    header = not os.path.exists(CSV_PATH)
    df.to_csv(CSV_PATH, mode=mode, header=header, index=False)

# ========= LOAD IMAGE PAIRS =========
all_imgs = list_images(IMAGE_DIR)
img_map = {}

for fname in all_imgs:
    name, ext = os.path.splitext(fname)
    if name.endswith("_gt"):
        base = name[:-3]
        img_map.setdefault(base, {})["gt"] = fname
    elif name.endswith("_result"):
        base = name[:-7]
        img_map.setdefault(base, {})["result"] = fname

pairs = [(base, files["gt"], files["result"]) for base, files in img_map.items() if "gt" in files and "result" in files]
total = len(pairs)

# ========= SESSION STATE =========
if "idx" not in st.session_state:
    st.session_state.idx = 0

# ========= HEADER =========
st.markdown("<h1 style='text-align:center;color:var(--accent)'>MANAKAH YANG LEBIH JERNIH?</h1>", unsafe_allow_html=True)
st.markdown(f"""
<div style="
    padding:1.5rem;
    background:var(--secondary-background-color);
    border-radius:1rem;
    margin-bottom:1.5rem;
    font-size:1.05rem;
    line-height:1.7;
    color:var(--text-color);
">
  <h3 style="color:var(--primary-color); margin-top:0;">🧠 Apa ini?</h3>
  <p>
    Ini adalah kuis sederhana untuk melihat apakah manusia bisa membedakan gambar asli dan gambar yang dihasilkan oleh AI.<br>
    Setiap soal menampilkan dua gambar: satu adalah <b>gambar asli</b>, dan satu lagi adalah <b>gambar hasil AI</b>.
  </p>
  <p>
    Tugas Anda adalah memilih gambar yang menurut Anda <b>lebih jernih</b>.<br>
    Penilaian ini akan membantu memahami seberapa baik kualitas hasil AI berdasarkan persepsi manusia.
  </p>

  <h4 style="color:var(--primary-color); margin-top:2rem;">🔍 Apa maksud "jernih"?</h4>
  <ul style="padding-left:1.2rem;">
    <li><b>Tampak alami</b> (tidak terlihat aneh atau buatan)</li>
    <li><b>Tajam</b> dan tidak buram</li>
    <li><b>Warna dan detailnya</b> nyaman dilihat</li>
  </ul>

  <h4 style="color:var(--primary-color); margin-top:2rem;">🎯 Cara bermain:</h4>
  <ol style="padding-left:1.4rem;">
    <li>Masukkan <b>Nama / ID</b> Anda.</li>
    <li>Lihat dua gambar di sisi <b>Kiri</b> dan <b>Kanan</b>.</li>
    <li>Pilih gambar yang menurut Anda <b>lebih jernih</b>.</li>
    <li>Klik <b>➡️ Berikutnya</b> untuk lanjut.</li>
    <li>Lanjutkan hingga semua gambar selesai.</li>
  </ol>
</div>
""", unsafe_allow_html=True)


# ========= USER INPUT =========
user = st.text_input("Masukkan Nama / ID Anda:")
if not user:
    st.stop()

# ========= DOWNLOAD MODE =========
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
    st.markdown(f"**Pasangan {idx + 1} dari {total}**")
    st.progress((idx + 1) / total)

    # Randomize position
    items = [("Asli", gt_file), ("Hasil AI", res_file)]
    random.shuffle(items)
    (left_label, left_file), (right_label, right_file) = items

    # Load and encode
    left_b64 = base64.b64encode(load_image_bytes(os.path.join(IMAGE_DIR, left_file))).decode()
    right_b64 = base64.b64encode(load_image_bytes(os.path.join(IMAGE_DIR, right_file))).decode()

    # Display
    st.markdown(f"""
        <div style="display:flex; gap:1%; margin-bottom:1rem;">
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

    # Form
    with st.form("vote_form", clear_on_submit=True):
        choice = st.radio("Mana yang tampak paling jernih (natural)?", ["Kiri", "Kanan"], horizontal=True)
        if st.form_submit_button("➡️  Berikutnya"):
            picked_label = left_label if choice == "Kiri" else right_label
            save_vote(user, base, picked_label)
            st.session_state.idx += 1
            st.rerun()

# ========= QUIZ COMPLETE =========
else:
    st.balloons()
    st.success("🎉 Selesai! Terima kasih atas partisipasi Anda.")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        if "user" in df.columns and "choice" in df.columns:
            user_df = df[df["user"] == user]
            if not user_df.empty:
                total_votes = len(user_df)
                ai_votes = (user_df["choice"] == 0).sum()
                percent_ai = int(round(100.0 * ai_votes / total_votes))

                # Determine message based on score
                if percent_ai >= 80:
                    msg = "Wah! AI berhasil mengelabui kamu hampir di semua gambar!"
                elif percent_ai >= 50:
                    msg = "Lumayan sering terkecoh. gambar AI terlihat cukup meyakinkan! Keren kan ??"
                elif percent_ai >= 20:
                    msg = "Kamu masih bisa membedakan dengan baik, tapi AI mulai mendekati kenyataan."
                else:
                    msg = "Hebat! Kamu cukup jeli dalam mengenali gambar buatan AI."

                st.markdown(f"""
                <div style="text-align:center; padding:2rem; background:#fffaf0; border-radius:1rem;">
                    <div style="font-size:4rem; font-weight:bold; color:var(--accent);">{percent_ai}%</div>
                    <div style="margin-top:1rem; font-size:1.2rem; font-weight:bold; color:#000;">gambar yang kamu pilih sebagai paling jernih adalah hasil dari AI.</div>
                    <div style="margin-top:1rem; font-size:1.1rem; color:#333;">{msg}</div>
                </div>
                """, unsafe_allow_html=True)

    if st.button("🔄 Mulai Ulang Quiz"):
        st.session_state.idx = 0
        st.rerun()
