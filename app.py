import streamlit as st
import json
import requests
from datetime import datetime

st.set_page_config(page_title="Sunrise Parish Y&A Zone", layout="centered", page_icon="⛪")

# Load data from your GitHub repo
data_url = "https://raw.githubusercontent.com/Adewah245/rccg-parish-data/main/data.json"
# Base URL for photos - UPDATE THIS to match where your photos are stored
photos_base_url = "https://raw.githubusercontent.com/Adewah245/rccg-parish-data/main/photos/"
# Logo URL - UPDATE THIS to match where your logo is stored
logo_url = "https://raw.githubusercontent.com/Adewah245/rccg-parish-data/main/logo.png"

# Display logo at the top
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image(logo_url, use_container_width=True)
    except:
        st.write("⛪")  # Fallback if logo fails to load

st.title("🏢 RCCG BENUE 2 SUNRISE PARISH")
st.header("YOUNG AND ADULTS ZONE")

st.markdown("---")

try:
    data = requests.get(data_url).json()
    members_list = data.get("members", [])
    messages = data.get("messages", [])
    last_update = data.get("last_update", "Unknown")
except:
    st.error("Unable to load latest data. Please contact the Youth President.")
    st.stop()

# Convert list to dictionary for easier handling
members = {}
for member in members_list:
    name = member.get("name", "Unknown")
    members[name] = member

# Latest Message
if messages:
    latest = messages[-1]
    with st.expander("📢 LATEST PARISH MESSAGE", expanded=True):
        st.markdown(f"**{latest['text']}**")
        st.caption(f"Sent on: {latest['date']}")
else:
    with st.expander("📢 PARISH MESSAGE", expanded=True):
        st.info("No announcement yet. Stay tuned!")

st.markdown("---")

st.success(f"**Total Members: {len(members)}** | Last updated: {last_update}")

# Search
search = st.text_input("🔍 Search by name or phone")
filtered = members

if search:
    search_lower = search.lower()
    filtered = {}
    for name, info in members.items():
        name_match = search_lower in name.lower()
        phone_match = search_lower in info.get("phone", "").lower()
        if name_match or phone_match:
            filtered[name] = info

if not filtered:
    st.warning("No members found.")
else:
    st.markdown(f"### 📋 Members List ({len(filtered)} shown)")
    # Sort alphabetically by name (case-insensitive)
    sorted_members = sorted(filtered.items(), key=lambda x: x[0].lower())
    for i, (name, info) in enumerate(sorted_members, 1):
        with st.expander(f"{i}. {name.title()}"):
            # Create two columns for photo and info
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display photo if available
                photo = info.get('photo', '')
                if photo and photo != "Photo copy failed" and photo.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    photo_url = photos_base_url + photo
                    try:
                        st.image(photo_url, width=150, caption=name.title())
                    except:
                        st.write("📷")
                        st.caption("Photo unavailable")
                else:
                    st.write("👤")
                    st.caption("No photo")
            
            with col2:
                st.write(f"**📱 Phone:** {info.get('phone', 'N/A')}")
                st.write(f"**📍 Address:** {info.get('address', 'N/A')}")
                if info.get('email'):
                    st.write(f"**📧 Email:** {info.get('email')}")
                if info.get('birthday'):
                    st.write(f"**🎂 Birthday:** {info.get('birthday')}")
                st.caption(f"✅ Joined: {info.get('joined', 'Unknown')}")

st.markdown("---")
st.caption("Managed by Youth President | For inquiries, contact the admin · God bless you! ✝️")
