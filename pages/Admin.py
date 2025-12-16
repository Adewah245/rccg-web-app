import streamlit as st
import json
import requests
from datetime import datetime
import base64

st.set_page_config(page_title="Admin Panel - RCCG Parish", layout="wide", page_icon="🔐")

# ==================== CONFIGURATION ====================
GITHUB_REPO = "Adewah245/rccg-parish-data"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")  # Will be set in Streamlit secrets
DATA_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/data.json"
PHOTOS_PATH = "photos/"

# ==================== HELPER FUNCTIONS ====================

def get_file_from_github(path):
    """Get file content from GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        return base64.b64decode(content['content']).decode('utf-8'), content['sha']
    return None, None

def save_to_github(path, content, message, sha=None):
    """Save file to GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "message": message,
        "content": base64.b64encode(content.encode() if isinstance(content, str) else content).decode()
    }
    
    if sha:
        data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

def upload_photo_to_github(photo_bytes, filename):
    """Upload photo to GitHub"""
    path = f"{PHOTOS_PATH}{filename}"
    return save_to_github(path, photo_bytes, f"Upload photo: {filename}")

def load_data():
    """Load data from GitHub"""
    content, sha = get_file_from_github("data.json")
    if content:
        return json.loads(content), sha
    return {"members": [], "messages": [], "last_update": ""}, None

def save_data(data, sha):
    """Save data to GitHub"""
    data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = json.dumps(data, indent=4)
    return save_to_github("data.json", content, "Update data", sha)

# ==================== AUTHENTICATION ====================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Admin Login")
    st.markdown("### RCCG Sunrise Parish - Admin Panel")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if st.button("Login"):
        # Change this to your desired password
        if password == st.secrets.get("ADMIN_PASSWORD", "rccg2024"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid password!")
    
    st.info("💡 Default password: rccg2024 (Change this in Streamlit secrets)")
    st.stop()

# ==================== MAIN ADMIN PANEL ====================

st.title("🏢 RCCG Parish Admin Panel")
st.caption("Manage members, photos, and announcements")

if st.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.markdown("---")

# Check GitHub token
if not GITHUB_TOKEN:
    st.error("⚠️ GitHub token not configured! Please add GITHUB_TOKEN to Streamlit secrets.")
    st.info("""
    **How to add GitHub token:**
    1. Go to your Streamlit app settings
    2. Click on "Secrets" in the left menu
    3. Add: `GITHUB_TOKEN = "your_github_token_here"`
    4. Get token from: https://github.com/settings/tokens
    """)
    st.stop()

# Load data
try:
    data, sha = load_data()
    members_list = data.get("members", [])
    messages = data.get("messages", [])
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# ==================== TABS ====================

tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Member", "📋 View/Edit Members", "📢 Announcements", "⚙️ Settings"])

# ==================== TAB 1: ADD MEMBER ====================
with tab1:
    st.header("➕ Add New Member")
    
    with st.form("add_member_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="e.g., John Doe")
            phone = st.text_input("Phone Number *", placeholder="e.g., 09012345678")
            email = st.text_input("Email", placeholder="e.g., john@example.com")
        
        with col2:
            address = st.text_input("Address *", placeholder="e.g., 123 Main Street")
            birthday = st.text_input("Birthday", placeholder="e.g., 15-05-1990 (DD-MM-YYYY)")
            photo = st.file_uploader("Upload Photo", type=['jpg', 'jpeg', 'png', 'gif'])
        
        submitted = st.form_submit_button("➕ Add Member")
        
        if submitted:
            if not name or not phone or not address:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                # Create member object
                photo_filename = ""
                if photo:
                    # Create filename: Name_Phone.extension
                    safe_name = name.lower().replace(" ", "_")
                    ext = photo.name.split(".")[-1]
                    photo_filename = f"{safe_name}_{phone}.{ext}"
                    
                    # Upload photo to GitHub
                    with st.spinner("Uploading photo..."):
                        if upload_photo_to_github(photo.read(), photo_filename):
                            st.success(f"✅ Photo uploaded: {photo_filename}")
                        else:
                            st.error("❌ Photo upload failed")
                            photo_filename = "Photo upload failed"
                
                new_member = {
                    "name": name.lower(),
                    "phone": phone,
                    "address": address,
                    "joined": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                if email:
                    new_member["email"] = email
                if birthday:
                    new_member["birthday"] = birthday
                if photo_filename:
                    new_member["photo"] = photo_filename
                
                # Add to members list
                members_list.append(new_member)
                data["members"] = members_list
                
                # Save to GitHub
                with st.spinner("Saving member data..."):
                    if save_data(data, sha):
                        st.success(f"✅ Member '{name}' added successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to save member data")

# ==================== TAB 2: VIEW/EDIT MEMBERS ====================
with tab2:
    st.header("📋 Members Directory")
    st.info(f"Total Members: {len(members_list)}")
    
    # Search
    search = st.text_input("🔍 Search members", placeholder="Search by name or phone")
    
    # Filter members
    filtered_members = members_list
    if search:
        search_lower = search.lower()
        filtered_members = [m for m in members_list if 
                          search_lower in m.get("name", "").lower() or 
                          search_lower in m.get("phone", "")]
    
    # Sort alphabetically
    filtered_members = sorted(filtered_members, key=lambda x: x.get("name", "").lower())
    
    st.markdown(f"**Showing {len(filtered_members)} member(s)**")
    
    for idx, member in enumerate(filtered_members):
        with st.expander(f"👤 {member.get('name', 'Unknown').title()} - {member.get('phone', 'N/A')}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if member.get('photo') and member['photo'] != "Photo upload failed":
                    photo_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{PHOTOS_PATH}{member['photo']}"
                    try:
                        st.image(photo_url, width=150)
                    except:
                        st.write("📷 Photo unavailable")
                else:
                    st.write("👤 No photo")
            
            with col2:
                st.write(f"**📱 Phone:** {member.get('phone', 'N/A')}")
                st.write(f"**📍 Address:** {member.get('address', 'N/A')}")
                st.write(f"**📧 Email:** {member.get('email', 'N/A')}")
                st.write(f"**🎂 Birthday:** {member.get('birthday', 'N/A')}")
                st.caption(f"✅ Joined: {member.get('joined', 'Unknown')}")
            
            # Delete button
            if st.button(f"🗑️ Delete {member.get('name', 'this member')}", key=f"del_{idx}"):
                members_list.remove(member)
                data["members"] = members_list
                if save_data(data, sha):
                    st.success(f"✅ Deleted {member.get('name', 'member')}")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete member")

# ==================== TAB 3: ANNOUNCEMENTS ====================
with tab3:
    st.header("📢 Parish Announcements")
    
    # Show existing messages
    if messages:
        st.subheader("Current Messages")
        for idx, msg in enumerate(reversed(messages)):
            with st.expander(f"📅 {msg['date']} - {msg['text'][:50]}..."):
                st.write(msg['text'])
                if st.button(f"🗑️ Delete", key=f"msg_{idx}"):
                    messages.remove(msg)
                    data["messages"] = messages
                    if save_data(data, sha):
                        st.success("✅ Message deleted")
                        st.rerun()
    else:
        st.info("No announcements yet")
    
    st.markdown("---")
    st.subheader("📝 Post New Announcement")
    
    with st.form("announcement_form"):
        message_text = st.text_area("Message", placeholder="Enter your announcement here...", height=150)
        submit_msg = st.form_submit_button("📢 Post Announcement")
        
        if submit_msg:
            if message_text:
                new_message = {
                    "text": message_text,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                messages.append(new_message)
                data["messages"] = messages
                
                if save_data(data, sha):
                    st.success("✅ Announcement posted!")
                    st.rerun()
                else:
                    st.error("❌ Failed to post announcement")
            else:
                st.error("❌ Please enter a message")

# ==================== TAB 4: SETTINGS ====================
with tab4:
    st.header("⚙️ Settings")
    
    # Logo Upload Section
    st.subheader("🎨 Church Logo")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Show current logo if exists
        logo_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/logo.png"
        try:
            st.image(logo_url, caption="Current Logo", width=200)
        except:
            st.info("No logo uploaded yet")
    
    with col2:
        st.write("**Upload/Update Church Logo**")
        logo_file = st.file_uploader("Choose logo image", type=['png', 'jpg', 'jpeg'], key="logo_upload")
        
        if logo_file:
            # Show preview
            st.image(logo_file, caption="Preview", width=200)
            
            if st.button("⬆️ Upload Logo"):
                with st.spinner("Uploading logo..."):
                    # Determine file extension
                    ext = logo_file.name.split(".")[-1]
                    logo_filename = f"logo.{ext}"
                    
                    # Upload to GitHub root
                    logo_path = logo_filename
                    logo_url_api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{logo_path}"
                    
                    # Check if logo already exists (to get SHA for update)
                    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
                    existing = requests.get(logo_url_api, headers=headers)
                    existing_sha = existing.json().get('sha') if existing.status_code == 200 else None
                    
                    # Upload
                    logo_bytes = logo_file.read()
                    if save_to_github(logo_path, logo_bytes, "Update church logo", existing_sha):
                        st.success("✅ Logo uploaded successfully!")
                        st.balloons()
                        st.info(f"Logo URL: https://raw.githubusercontent.com/{GITHUB_REPO}/main/{logo_filename}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to upload logo")
    
    st.markdown("---")
    st.subheader("📊 Statistics")
    st.metric("Total Members", len(members_list))
    st.metric("Total Announcements", len(messages))
    st.metric("Last Updated", data.get("last_update", "Unknown"))
    
    st.markdown("---")
    st.subheader("🔗 Repository Info")
    st.write(f"**GitHub Repo:** {GITHUB_REPO}")
    st.write(f"**Data URL:** https://raw.githubusercontent.com/{GITHUB_REPO}/main/data.json")
    st.write(f"**Photos Path:** {PHOTOS_PATH}")
    
    st.markdown("---")
    st.subheader("💾 Backup Data")
    if st.button("📥 Download Backup"):
        backup_data = json.dumps(data, indent=4)
        st.download_button(
            label="⬇️ Download data.json",
            data=backup_data,
            file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

st.markdown("---")
st.caption("🏢 RCCG Benue 2 Sunrise Parish - Admin Panel | God bless you! ✝️")
