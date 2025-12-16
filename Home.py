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
    members = data.get("members", {})
    messages = data.get("messages", [])
    last_update = data.get("last_update", "Unknown")
except:
    st.error("Unable to load latest data. Please contact the Youth President.")
    st.stop()

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
    filtered = {n: info for n, info in members.items() if search_lower in n.lower() or search_lower in info["phone"].lower()}

if not filtered:
    st.warning("No members found.")
else:
    st.markdown(f"### 📋 Members List ({len(filtered)} shown)")
    st.markdown("---")
    for i, (name, info) in enumerate(sorted(filtered.items()), 1):
        st.markdown(f"**{i}. {name}**")
        st.markdown(f"**Phone:** {info['phone']}")
        st.markdown(f"**Address:** {info['address']}")
        st.markdown(f"**Joined:** {info['joined']}")
        st.markdown("")  # blank line
        st.markdown("---")  # separator line
