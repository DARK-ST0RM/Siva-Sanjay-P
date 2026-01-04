# Siva-Sanjay-P
Mini Project

Track E : Booking time for consultant
I chose this track to demonstrate a real-world booking workflow where consultants manage availability and clients request appointments. This track allowed me to design a simple yet realistic approval-based booking system with clear user roles.

Features Implemented:
1.Manual login for Consultant and Client roles
2.Consultant can create availability slots
3.Consultant can view all their slots
4.Client can view available slots
5.Client can request a booking
6.Booking status flow: available -> pending -> booked
7.Consultant can confirm pending bookings
8.Client sees real-time booking status
9.Friendly UI with clear status indicators
10.SQLite database persistence

Tech Stack:
Frontend: Streamlit
Backend: Flask (REST API)
Database: SQLite
Language: Python
API Communication: REST (JSON over HTTP)

How to run locally:
cd consultant-booking
cd backend -> python app.py
cd frontend -> streamlit run app.py

API Endpoints List:

POST /api/slots
GET /api/slots
GET /api/slots?consultant=<consultant_username>
POST /api/slots/<slot_id>/request
POST /api/slots/<slot_id>/confirm

Table: slots
Fields: id,consultant,date,start_time,end_time,status,booked_by,requested_at

AI usage log:
AI was used for assistance in drafting backend APIs and frontend UI. 
All logic, role handling, and booking flow were reviewed, tested, and refined manually.

Trade-offs and next improvements:

1.Used simple authentication to keep the system lightweight.
2.No real-time updates; page refresh needed after actions.
3.Basic UI with Streamlit; can be enhanced using React.
4.SQLite database; can be upgraded to PostgreSQL.
5.Add notifications, role-based auth, and calendar integration in future.





