# Real-Time Poll App with Web Push Notifications

A modern, full-stack voting application featuring real-time **Firebase Cloud Messaging (FCM)** notifications, a Flask backend, and a sleek UI.

---

## Project Journey & Learning

This project represents over **20+ hours** of intensive development. My goal was to move beyond simple static sites and master the complexities of **asynchronous communication** and **cloud-based messaging**.

### Key Challenges Overcome

- **The Notification Hurdle:**  
  Spent 4 days+ mastering **Firebase Cloud Messaging**. Learned to manage Service Workers, VAPID keys, and browser security restrictions to ensure reliable delivery on both Desktop and Android.

- **Full-Stack Logic:**  
  Designed the complete data flow — from user authentication to database relationships (SQL) and real-time frontend updates.

- **Modern UI/UX:**  
  Built a specialized "Enable Notifications" workflow to handle modern browser requirements for user-triggered permissions.

---

## Core Features

- **Push Notifications:** Instant alerts sent to subscribed devices whenever a new poll is created  
- **Secure Voting:** Backend logic to prevent duplicate voting and ensure data integrity  
- **Live Dashboard:** Clean results view showing participant choices and feedback  
- **Design:** Dark-themed UI with modern aesthetics and mobile responsiveness  

---

## Tech Stack

- **Backend:** Python (Flask)  
- **Frontend:** HTML5, CSS3 (Flexbox/Grid), JavaScript (ES6+ / Fetch API)  
- **Database:** SQLite3  
- **Cloud Messaging:** Firebase Cloud Messaging (FCM)  
- **Hosting:** Render  

---

## System Architecture

1. **Client-Side:** Registers a **Service Worker** to handle background push events  
2. **Server-Side:** Flask server communicates with the **Firebase Admin SDK** to trigger notifications  
3. **Database:** Stores users, polls, and unique FCM tokens for targeted delivery  

---

## Architectural Note

**Database Persistence:**  
This app is hosted on **Render's Free Tier**, which uses an ephemeral file system. While SQLite works perfectly for local logic, the data resets when the server spins down.

- **Future Scaling:**  
  A production-ready version would migrate to a persistent cloud database like **MongoDB Atlas** or **PostgreSQL**, but no plans right now.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/NILAY-KS07/poll-app.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Firebase Service Account keys as environment variables.

4. Run the app:
```bash
python app.py
```

## Made By

Nilay Kumar Shrivastava

## Thank You
