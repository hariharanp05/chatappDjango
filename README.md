# YourSpace 🪐

YourSpace is a real-time, space-themed chat application built with Django and Django Channels. It allows users to participate in public discussions, send private messages, share files, and manage connections with an elegant UI inspired by modern design aesthetics.

## 🌟 Features

- 🔒 Private Messaging with Message Requests
- 💬 Public Chat Rooms
- 📁 File Uploads (images, documents)
- 🧾 Notifications System
- 👤 User Profiles with Block/Unblock Feature
- 🪐 Animated and Responsive UI (space-inspired)
- ⚡ Real-time Communication using WebSockets
- 🛠️ Admin Management

## 🖥️ Technologies Used

- Django
- Django Channels
- WebSocket (with JavaScript)
- SQLite
- HTML, CSS (custom + animation)
- JavaScript
- Tailwind CSS (optional)

## 🚀 Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/hariharanp05/chatappDjango.git
   cd chatappDjango
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate  # For Linux/macOS
   env/scripts/activate     # For Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Run the server:
   ```bash
   python manage.py runserver
   ```

6. Visit:  
   ```
   http://127.0.0.1:8000/
   ```

## 🖼️ UI References

> The design of YourSpace is inspired by modern UI elements and layouts, taking influence from reference designs provided during development. These include animated backgrounds, clean layout sections, and a dark theme optimized for focus and readability.



## 📂 Folder Structure (Important)

```bash
chatappDjango/
├── chat/                  # Chat app with consumers, models, views
├── media/uploads/        # Uploaded user files
├── templates/chat/       # HTML templates
├── static/chat/          # CSS & JS
├── db.sqlite3            # SQLite Database
├── manage.py
└── requirements.txt
```


