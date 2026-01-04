import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"

# ----------------- Manual Users -----------------
users = {
    "consultant1": {"password": "pass123", "role": "consultant"},
    "consultant2": {"password": "pass123", "role": "consultant"},
    "client1": {"password": "pass123", "role": "client"},
    "client2": {"password": "pass123", "role": "client"},
    "client3": {"password": "pass123", "role": "client"},
}

# ----------------- Session State -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ----------------- Login -----------------
if not st.session_state.logged_in:
    st.title("🔑 Consultant Booking System")
    st.write("Please log in to continue")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# ----------------- Consultant Dashboard -----------------
if st.session_state.role == "consultant":
    st.title(f"👨‍💼 Consultant Dashboard - {st.session_state.username}")
    st.markdown("---")

    # Create Slots
    with st.expander("📅 Create New Availability Slot", expanded=True):
        with st.form("create_slot_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                date = st.date_input("Date")
            with col2:
                start_time = st.time_input("Start Time")
            with col3:
                end_time = st.time_input("End Time")
            submit = st.form_submit_button("Create Slot")
            if submit:
                if start_time >= end_time:
                    st.error("❌ End time must be after start time")
                else:
                    payload = {
                        "consultant": st.session_state.username,
                        "date": str(date),
                        "start_time": str(start_time),
                        "end_time": str(end_time)
                    }
                    res = requests.post(f"{BACKEND_URL}/api/slots", json=payload)
                    if res.status_code == 200:
                        st.success("✅ Slot created successfully")
                        st.rerun()
                    else:
                        st.error(res.json().get("error"))

    st.markdown("---")

    # Show all slots of this consultant
    st.subheader("🟡 Your Slots & Pending Bookings")
    res = requests.get(f"{BACKEND_URL}/api/slots", params={"consultant": st.session_state.username})
    slots = res.json()

    if not slots:
        st.info("No slots created yet")
    else:
        for slot in slots:
            col1, col2, col3, col4 = st.columns([2,2,2,2])
            status_display = slot["status"]
            color = "black"
            if status_display == "pending":
                status_display = "⏳ Pending approval"
                color = "orange"
            elif status_display == "booked":
                status_display = "✅ Booked"
                color = "green"
            else:
                status_display = "🟢 Available"
                color = "blue"

            col1.markdown(f"📅 **{slot['date']}**")
            col2.markdown(f"⏰ **{slot['start_time']} - {slot['end_time']}**")
            col3.markdown(f"<span style='color:{color}; font-weight:bold'>{status_display}</span>", unsafe_allow_html=True)
            col4.markdown(f"Requested by: {slot.get('booked_by','-')}")

            # Friendly Confirm Button
            if slot["status"] == "pending":
                if col4.button(f"✅ Confirm {slot['id']}", key=f"confirm{slot['id']}"):
                    res = requests.post(f"{BACKEND_URL}/api/slots/{slot['id']}/confirm")
                    if res.status_code == 200:
                        st.success("✅ Slot confirmed successfully")
                        st.rerun()
                    else:
                        st.error(res.json().get("error"))

# ----------------- Client Dashboard -----------------
elif st.session_state.role == "client":
    st.title(f"👤 Client Dashboard - {st.session_state.username}")
    st.markdown("---")

    st.subheader("Available Slots")
    res = requests.get(f"{BACKEND_URL}/api/slots")
    slots = res.json()

    # Filter slots for client view
    available_slots = [
        s for s in slots 
        if s["status"] == "available" 
        or (s["status"] in ["pending","booked"] and s.get("booked_by") == st.session_state.username)
    ]

    if not available_slots:
        st.info("No slots available")
    else:
        for slot in available_slots:
            col1, col2, col3, col4 = st.columns([2,2,2,2])
            status_display = slot["status"]
            color = "black"
            if slot["status"] == "pending" and slot.get("booked_by") == st.session_state.username:
                status_display = "⏳ Booking requested"
                color = "orange"
            elif slot["status"] == "pending":
                status_display = "⏳ Pending approval"
                color = "orange"
            elif slot["status"] == "booked" and slot.get("booked_by") == st.session_state.username:
                status_display = "✅ Confirmed"
                color = "green"
            else:
                status_display = "🟢 Available"
                color = "blue"

            col1.markdown(f"📅 **{slot['date']}**")
            col2.markdown(f"⏰ **{slot['start_time']} - {slot['end_time']}**")
            col3.markdown(f"<span style='color:{color}; font-weight:bold'>{status_display}</span>", unsafe_allow_html=True)
            col4.markdown(f"👨‍💼 {slot['consultant']}")

            # Friendly Request Button
            if slot["status"] == "available":
                if col4.button(f"🟢 Request {slot['id']}", key=f"request{slot['id']}"):
                    payload = {"client_username": st.session_state.username}
                    res = requests.post(f"{BACKEND_URL}/api/slots/{slot['id']}/request", json=payload)
                    if res.status_code == 200:
                        st.success("✅ Booking requested successfully")
                        st.rerun()
                    else:
                        st.error(res.json().get("error"))
