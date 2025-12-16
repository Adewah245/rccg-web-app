import streamlit as st
import json
import requests
from datetime import datetime

st.set_page_config(page_title="Sunrise Parish Y&A Zone", layout="centered")

st.title("🏢 RCCG BENUE 2 SUNRISE PARISH")
st.header("YOUNG AND ADULTS ZONE")

st.markdown("---")

# Load data from your GitHub repo
data_url = "https://raw.githubusercontent.com/Adewah245/rccg-parish-data/main/data.json"

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
    for i, (name, info) in enumerate(sorted(filtered.items()), 1):
        with st.expander(f"{i}. {name.title()}"):
            st.write(f"**📱 Phone:** {info.get('phone', 'N/A')}")
            st.write(f"**📍 Address:** {info.get('address', 'N/A')}")
            if info.get('email'):
                st.write(f"**📧 Email:** {info.get('email')}")
            if info.get('birthday'):
                st.write(f"**🎂 Birthday:** {info.get('birthday')}")
            st.caption(f"✅ Joined: {info.get('joined', 'Unknown')}")

st.markdown("---")
st.caption("Managed by Youth President | For inquiries, contact the admin · God bless you! ✝️")

