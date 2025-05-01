# 💬 Advanced Real-Time Chat App 🚀

Welcome to **Advanced Real-Time Chat**, a sleek, powerful chat application built using **Flask**, **Socket.IO**, and **Vanilla JS**. Designed to support **multiple rooms**, **private messaging**, and **live user tracking**, this app is your go-to for real-time web communication! 🔥

---

## ✨ Features

✅ **Multi-Room Support** — Seamlessly switch between chat rooms.  
🧍‍♂️🧍‍♀️ **Active User Tracking** — See who's online in real-time.  
📩 **Private Messaging** — DM anyone with a simple `@username`.  
🪄 **Smooth UI/UX** — Modern design with animations & transitions.  
🧠 **Persistent Room History** — Messages are stored per room during the session.  
📱 **Responsive Layout** — Mobile & desktop friendly.

---

## 🛠️ Tech Stack

| Frontend             | Backend           | Real-Time Engine  |
| -------------------- | ----------------- | ----------------- |
| HTML5 + CSS3 + JS ✨ | Python + Flask 🐍 | Flask-SocketIO ⚡ |

---

## 📁 Project Structure

/chat-app/ │ ├── static/ │ ├── styles.css # Styling for chat UI 🎨 │ └── chat.js # Frontend socket logic & UI events 🧠 │ ├── templates/ │ └── index.html # Main chat UI rendered via Flask 🧾 │ ├── app.py # Flask app with SocketIO events 🧩 └── README.md # This file 📘

# 🎮 How to Use

💬 Type messages and hit Send or press Enter.

📥 Want to send a private message? Type: @username your message.

📁 Switch between rooms by clicking on room names.

🟢 Watch users join/leave in real time under Online Users.

🧼 Room message history clears only when you refresh or leave the room.

# 📌 Code Highlights

Dynamic Message Styling: Based on type — own, other, private, or system.

Room Switching: Persists session messages using JS objects.

Live User List: Updated in real-time using active_users event.

Animations: Messages fade in smoothly with @keyframes fadeIn.

# 💡 Future Improvements

🗃️ Store chat history in a database (SQLite, MongoDB, etc).

🔐 Add user authentication (login/register).

📱 Build a mobile app version using React Native or Flutter.

🎨 Add emojis, file sharing, and typing indicators.


# 👨‍💻 Developed By

Me! 🙌
This is a great foundation for your Flask + SocketIO portfolio.