\# 🗳️ Real-Time Poll App with Web Push Notifications



A modern, full-stack voting application featuring real-time \*\*Firebase Cloud Messaging (FCM)\*\* notifications, a Flask backend, and a sleek UI.



\---



\##Project Journey \& Learning

This project represents over \*\*35+ hours\*\* of intensive development. My goal was to move beyond simple static sites and master the complexities of \*\*asynchronous communication\*\* and \*\*cloud-based messaging\*\*.



\###Key Challenges Overcome:

\* \*\*The Notification Hurdle:\*\* Spent 7 days mastering \*\*Firebase Cloud Messaging\*\*. I learned to manage Service Workers, VAPID keys, and browser security restrictions to ensure reliable delivery on both Desktop and Android.

\* \*\*Full-Stack Logic:\*\* Designed the complete data flow: from User Authentication to Database relationships (SQL) and real-time frontend updates.

\* \*\*Modern UI/UX:\*\* Built a specialized "Enable Notifications" workflow to handle modern browser requirements for user-triggered permissions.



\---



\##Core Features

\* \*\*Push Notifications:\*\* Instant alerts sent to subscribed devices whenever a new poll is created.

\* \*\*Secure Voting:\*\* Backend logic to prevent duplicate voting and ensure data integrity.

\* \*\*Live Dashboard:\*\* A clean results view showing participant choices and feedback.

\* \*\*Design:\*\* A professional, dark-themed UI focused on modern aesthetics and mobile responsiveness.



\---



\##Tech Stack

\* \*\*Backend:\*\* Python (Flask)

\* \*\*Frontend:\*\* HTML5, CSS3 (Flexbox/Grid), JavaScript (ES6+ / Fetch API)

\* \*\*Database:\*\* SQLite3

\* \*\*Cloud Messaging:\*\* Firebase Cloud Messaging (FCM)

\* \*\*Hosting:\*\* Render



\---



\##System Architecture

1\. \*\*Client-Side:\*\* Registers a \*\*Service Worker\*\* to handle background push events.

2\. \*\*Server-Side:\*\* The Flask server communicates with the \*\*Firebase Admin SDK\*\* to trigger notifications.

3\. \*\*Database:\*\* Manages users, polls, and unique FCM tokens to target specific devices.



\---



\##Architectural Note

\*\*Database Persistence:\*\* This app is hosted on \*\*Render's Free Tier\*\*, which uses an ephemeral file system. While the SQLite database handles local logic perfectly, the data resets when the server spins down. 

\* \*Future Scaling:\* A production version would migrate to a persistent cloud database like \*\*MongoDB Atlas\*\* or \*\*PostgreSQL\*\*.



\---



\##Installation

1\. Clone the repository:

&#x20;  ```bash

&#x20;  git clone \[https://github.com/NILAY-KS07/poll-app.git](https://github.com/NILAY-KS07/poll-app.git)```



2\. Install dependencies:

&#x20;  ```bash

&#x20;  pip install -r requirements.txt```



3\. Set up your Firebase Service Account keys as environment variables.



4\. Run the app:

&#x20;  ```bash

&#x20;  python app.py



\##Made By:

\*\*Nilay Kumar Shrivastava\*\*



\##Thankyou

