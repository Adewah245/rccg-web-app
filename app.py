import streamlit as st
import json
import os

st.set_page_config(page_title="RCCG Sunrise Parish", layout="wide")

DATA_FILE = "parish_members.json"
PHOTOS_DIR = "member_photos"
LOGO_FILE = "logo.txt"

def load_members():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def load_logo():
    if os.path.exists(LOGO_FILE):
        with open(LOGO_FILE, "r") as f:
            return f.read()
    return ""

members = load_members()

# ---- HEADER ----
logo = load_logo()
if logo:
    st.text(logo)

st.markdown("## ⛪ RCCG Benue 2 Sunrise Parish – Young & Adults Zone")
st.markdown(f"👥 **Total Members:** {len(members)}")
st.divider()

# ---- SEARCH ----
search = st.text_input("🔍 Search by name or phone")

filtered = []
for m in members:
    if search.lower() in m["name"].lower() or search in m["phone"]:
        filtered.append(m)

st.markdown(f"### Members List ({len(filtered)} shown)")

# ---- DISPLAY MEMBERS ----
for m in filtered:
    col1, col2 = st.columns([1, 3])

    photo = m.get("photo", "No photo")
    photo_path = os.path.join(PHOTOS_DIR, photo)

    with col1:
        if photo != "No photo" and os.path.exists(photo_path):
            st.image(photo_path, width=120)
        else:
            st.info("No photo")

    with col2:
        st.markdown(f"### 👤 {m['name']}")
        st.write(f"📞 Phone: {m['phone']}")
        st.write(f"✉️ Email: {m.get('email','Not provided')}")
        st.write(f"🏠 Address: {m['address']}")
        st.write(f"🎂 Birthday: {m['birthday']}")
        st.write(f"📅 Joined: {m['joined']}")

    st.divider()
