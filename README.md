# Flask Casdoor Authentication

This Flask web application demonstrates the integration with Casdoor for authentication. 
It utilizes the [Python Casdoor SDK](https://github.com/casdoor/casdoor-python-sdk) 
to handle authentication flows.

## 🌟 Features

- ✅ User authentication via Casdoor.
- 🔒 Session management with Flask-Session.
- 🎨 Login and home pages.
- 🚹 Profile page to view user details.

## 🚀 Setup & Installation

### 1. Clone the repository:

```bash
git clone [your-repository-url]
cd [your-repository-directory]
```

### 2. Create and activate a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the required packages:

```
pip install -r requirements.txt
```

### 4. Set up your environment variables:

Copy the `.env.example` to `.env` and fill out the required Casdoor credentials and configurations.

### 5. Run the application:

```
python app.py
```

Your application will be running on `http://127.0.0.1:8080/`.