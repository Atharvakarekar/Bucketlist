import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import base64
import random
import calendar
import json
import os

# --- Initial Setup ---
st.set_page_config(page_title="Bucket List App", layout="wide")
st.title("🗂️ Bucket List")

DATA_FILE = "bucket_list_data.json"

# --- Load from file if exists ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# --- Save to file ---
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, default=str)

if 'bucket_list' not in st.session_state:
    st.session_state.bucket_list = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
tags_filter = st.sidebar.multiselect("Filter by Tags", options=['Travel', 'Adventure', 'Personal', 'Career'])
priority_filter = st.sidebar.selectbox("Filter by Priority", options=["All", "High", "Medium", "Low"])

# --- Add New Bucket List Item ---
st.subheader("Add New Item")
with st.form("add_form"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    category = st.selectbox("Category Tag", ["Travel", "Adventure", "Personal", "Career"])
    date = st.date_input("Target Date", datetime.date.today())
    time = st.time_input("Target Time", datetime.datetime.now().time())
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    invitees = st.text_input("Invitees (comma-separated)")
    completed = st.checkbox("Mark as Completed")
    subtasks = st.text_area("Subtasks (comma-separated)")
    attachment = st.file_uploader("Upload Attachment (image/video)", type=["png", "jpg", "jpeg", "mp4"])
    submit = st.form_submit_button("Add to List")

    if submit:
        new_item = {
            "Title": title,
            "Description": description,
            "Category": category,
            "Date": str(date),
            "Time": str(time),
            "Priority": priority,
            "Invitees": invitees.split(","),
            "Completed": completed,
            "Subtasks": subtasks.split(",") if subtasks else [],
            "Attachment": None,
            "AttachmentName": attachment.name if attachment else None
        }
        st.session_state.bucket_list.append(new_item)
        save_data(st.session_state.bucket_list)
        st.success("Item added to your bucket list!")

# --- AI Suggestions ---
if st.sidebar.button("🔍 Get AI Suggestions"):
    suggestions = [
        "Go hiking in the Alps", "Plant a tree in every country you visit", "Learn to cook a new cuisine",
        "Swim with dolphins", "Write a novel", "Go scuba diving in Bali", "Take a sabbatical year",
        "Watch the Northern Lights", "Build a personal robot", "Learn blacksmithing", "Skydive in Dubai",
        "Road trip through Iceland", "Master an instrument", "Start a community project", "Run a marathon",
        "Visit all 7 continents", "Make a short film", "Attend a silent meditation retreat",
        "Go to the Olympics", "Host a podcast series"
    ]
    st.sidebar.write(f"**Suggested:** {random.choice(suggestions)}")

# --- Leaderboard (Gamification Placeholder) ---
st.sidebar.markdown("\n**🏆 Leaderboard**")
leaderboard = sorted(st.session_state.bucket_list, key=lambda x: x['Completed'], reverse=True)
st.sidebar.write(f"Total Completed: {sum(1 for i in leaderboard if i['Completed'])}")

# --- Calendar View ---
st.subheader("🗓️ Calendar View")
calendar_data = {}
for item in st.session_state.bucket_list:
    date = datetime.datetime.strptime(item['Date'], "%Y-%m-%d").date()
    if date not in calendar_data:
        calendar_data[date] = []
    calendar_data[date].append(item['Title'])

for date in sorted(calendar_data.keys()):
    st.markdown(f"**{date.strftime('%B %d, %Y')}**")
    for task in calendar_data[date]:
        st.write(f"- {task}")

# --- Email/Push Reminders (Real Email via SMTP) ---
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.subheader("📣 Email Reminders")

def send_email(subject, body):
    try:
        sender = "your_email@gmail.com"
        password = "your_app_password"
        receiver = "your_email@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        st.success("Reminder email sent!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

reminders = []
today = datetime.date.today()
for item in st.session_state.bucket_list:
    task_date = datetime.datetime.strptime(item['Date'], "%Y-%m-%d").date()
    days_left = (task_date - today).days
    if 0 <= days_left <= 3:
        reminders.append(f"'{item['Title']}' is due in {days_left} day(s) on {item['Date']}")

if reminders and st.button("Send Email Reminder"):
    body = "".join(reminders)
    send_email("Upcoming Bucket List Reminders", body)

# --- Social Sharing (Simulated) ---
st.subheader("🎥 Share Your Bucket List")
share_text = "\n".join([
    f"{i['Title']} on {i['Date']} - {i['Category']}"
    for i in st.session_state.bucket_list
])
st.code(share_text)

st.markdown("**Share on:**")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"[Share on Twitter](https://twitter.com/intent/tweet?text={share_text.replace(' ', '%20').replace(chr(10), '%0A')})")
with col2:
    st.markdown(f"[Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=data:text/plain,{share_text.replace(' ', '%20').replace(chr(10), '%0A')})")
with col3:
    st.markdown(f"[Share on WhatsApp](https://wa.me/?text={share_text.replace(' ', '%20').replace(chr(10), '%0A')})")
with col4:
    mailto_link = f"mailto:?subject=My%20Bucket%20List&body={share_text.replace(' ', '%20').replace(chr(10), '%0A')}"
    st.markdown(f"[Share via Email]({mailto_link})")

st.success("Select a platform above to share your list!")

# --- Offline Sync Info ---
st.info("🌐 Offline Sync: Data will soon be available to download and auto-sync when internet is restored.")

# --- Display Bucket List ---
st.subheader("Your Bucket List")
filtered_list = [item for item in st.session_state.bucket_list if
                 (not tags_filter or item['Category'] in tags_filter) and
                 (priority_filter == "All" or item['Priority'] == priority_filter)]

for idx, item in enumerate(filtered_list):
    with st.expander(f"{item['Title']} - {item['Category']} ({item['Priority']})"):
        st.write(f"**Date:** {item['Date']} {item['Time']}")
        st.write(f"**Description:** {item['Description']}")
        st.write(f"**Invitees:** {', '.join(item['Invitees'])}")
        st.write("**Subtasks:**")
        for sub in item['Subtasks']:
            st.checkbox(sub, value=False, key=f"{idx}_{sub}")
        st.progress(100 if item['Completed'] else 0)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📝 Edit", key=f"edit_{idx}"):
                st.session_state.edit_index = idx
        with col2:
            if st.button(f"❌ Delete", key=f"delete_{idx}"):
                st.session_state.bucket_list.pop(idx)
                save_data(st.session_state.bucket_list)
                st.rerun()

# --- Edit Modal ---
if 'edit_index' in st.session_state:
    index = st.session_state.edit_index
    item = st.session_state.bucket_list[index]
    st.subheader(f"Edit Item: {item['Title']}")
    with st.form("edit_form"):
        new_title = st.text_input("Title", value=item['Title'])
        new_description = st.text_area("Description", value=item['Description'])
        new_category = st.selectbox("Category Tag", ["Travel", "Adventure", "Personal", "Career"], index=["Travel", "Adventure", "Personal", "Career"].index(item['Category']))
        new_date = st.date_input("Target Date", value=datetime.datetime.strptime(item['Date'], "%Y-%m-%d").date())
        time_str = item['Time'].split('.')[0]
        new_time = st.time_input("Target Time", value=datetime.datetime.strptime(time_str, "%H:%M:%S").time())
        new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(item['Priority']))
        new_invitees = st.text_input("Invitees (comma-separated)", value=", ".join(item['Invitees']))
        new_completed = st.checkbox("Mark as Completed", value=item['Completed'])
        new_subtasks = st.text_area("Subtasks (comma-separated)", value=", ".join(item['Subtasks']))
        submit_edit = st.form_submit_button("Update")

        if submit_edit:
            st.session_state.bucket_list[index] = {
                "Title": new_title,
                "Description": new_description,
                "Category": new_category,
                "Date": str(new_date),
                "Time": str(new_time),
                "Priority": new_priority,
                "Invitees": [i.strip() for i in new_invitees.split(",")],
                "Completed": new_completed,
                "Subtasks": [s.strip() for s in new_subtasks.split(",")],
                "Attachment": None,
                "AttachmentName": item.get('AttachmentName')
            }
            del st.session_state.edit_index
            save_data(st.session_state.bucket_list)
            st.success("Item updated!")
            st.rerun()

# --- Export Option ---
st.subheader("Export Bucket List")
export_format = st.selectbox("Select Export Format", ["CSV", "Excel"])
if st.button("Export"):
    df = pd.DataFrame(st.session_state.bucket_list)
    towrite = BytesIO()
    if export_format == "CSV":
        df.to_csv(towrite, index=False)
        mime = "text/csv"
        b64 = base64.b64encode(towrite.getvalue()).decode()
        href = f'<a href="data:{mime};base64,{b64}" download="bucket_list.csv">Download CSV</a>'
    else:
        df.to_excel(towrite, index=False)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        b64 = base64.b64encode(towrite.getvalue()).decode()
        href = f'<a href="data:{mime};base64,{b64}" download="bucket_list.xlsx">Download Excel</a>'
    st.markdown(href, unsafe_allow_html=True)

# # --- Sidebar Images for Inspiration ---
# st.sidebar.markdown("---")
# st.sidebar.image("https://source.unsplash.com/300x200/?travel", caption="Wander the World")
# st.sidebar.image("https://source.unsplash.com/300x200/?adventure", caption="Seek Adventure")
# st.sidebar.image("https://source.unsplash.com/300x200/?mountains,trekking", caption="Reach New Heights")
# st.sidebar.image("https://source.unsplash.com/300x200/?sunset,beach", caption="Catch the Moment")
# st.sidebar.markdown("---")
