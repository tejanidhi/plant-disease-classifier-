# 🌿 Plant Disease Detection Application

A simple application to upload plant images, detect diseases using machine learning models, and send SMS notifications if a disease is detected.

---

## 🚀 Quickstart Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/tejanidhi/plant-disease-classifier-.git
cd plant-disease-classifier
```

### Step 2: Setup Virtual Environment

Create and activate a virtual environment:

On Windows:
```bash
python -m venv env
env\Scripts\activate
```

On Mac/Linux:
```bash
python3 -m venv env
source venv/bin/activate
```

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

---

## 🚧 Run the Application

### Start the Backend

Navigate to the backend directory and start the FastAPI server:
```bash
cd backend
uvicorn main:app --reload
```

Backend will run at [`http://localhost:8000`](http://localhost:8000).

### Start the Frontend

In a new terminal, activate the virtual environment again and navigate to the frontend directory:
```bash
cd frontend
streamlit run app.py
```

Frontend will open at [`http://localhost:8501`](http://localhost:8501).

---

## 📂 Project Structure
```
project/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── app.py
├── .env
└── README.md
```

---

## 🛠️ Technologies Used

- **Backend:**
  - FastAPI
  - Twilio
  - OpenAI
  - Mistral

- **Frontend:**
  - Streamlit

- **Other:**
  - Python
  - Uvicorn

---

## 🌱 Environment Variables

Create a `.env` file in the backend directory with the following content:

```bash
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
DESTINATION_PHONE_NUMBER=receiver_phone_number
PIXTRAL_API_KEY=your_mixtral_api_key
```

---

## 🧪 Example Usage
- Upload a plant image using the frontend.
- The backend processes the image to detect any diseases.
- If a disease is detected, an SMS notification is sent, and recommendations appear on the frontend.

---

## 🐛 Troubleshooting

**Error: `python-multipart` not installed**
```bash
pip install python-multipart
```

**Backend not starting:**
- Ensure all dependencies are installed.
- Verify the `.env` file configuration.

**Frontend not connecting to backend:**
- Ensure backend is running at [`http://localhost:8000`](http://localhost:8000).
