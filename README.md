# 🤖 Streamlit ChatBot with Ollama & OCR

An advanced **AI-powered chatbot** built using **Streamlit** that integrates **Ollama models (like phi3, llama2, mistral)** for natural, context-aware conversations.  
It also features **OCR (Optical Character Recognition)** to extract text from **images and PDFs**, enabling intelligent document understanding.  

---

## ✨ Features

✅ **AI Chat Interface**
- Clean, ChatGPT-style conversational UI  
- Persistent chat history categorized by *Today, Yesterday, This Week*, etc.  

✅ **Ollama Integration**
- Runs on local Ollama models (e.g., `phi3`) for fast, privacy-friendly responses  
- Easily switch between models (phi3, llama2, mistral, etc.)  

✅ **OCR (Image & PDF Support)**
- Extracts text from uploaded images (`.png`, `.jpg`, `.jpeg`) and PDFs  
- Uses **Tesseract OCR** and **PyMuPDF** for accurate recognition  

✅ **Streamlit Sidebar**
- Create new chats  
- Search past conversations  
- Categorized chat history  
- Clear single or all chat sessions  

✅ **Beautiful UI**
- Custom HTML/CSS styling for elegant message bubbles  
- Chat input area supports file uploads directly  

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Frontend** | Streamlit, HTML, CSS |
| **Backend** | Python, Ollama API |
| **OCR** | pytesseract, PyMuPDF |
| **AI Models** | phi3 / llama2 / mistral (via Ollama) |

---

## ⚙️ Installation Guide

### 🪜 1️⃣ Clone the Repository
```bash
git clone https://github.com/Abhishek9978/Chatbot-infosys-springboard.git
cd Chatbot-infosys-springboard
````

### 🪜 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate    # On Windows
# or
source venv/bin/activate # On macOS/Linux
```

### 🪜 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> 🧩 *Dependencies include:*
> Streamlit, Ollama, pytesseract, Pillow, and PyMuPDF.

---

## 🧠 Setup Instructions

### 🔹 Install Tesseract OCR

* **Windows:** [Download from here](https://github.com/UB-Mannheim/tesseract/wiki)
* Default path used in code:

  ```
  C:\Program Files\Tesseract-OCR\tesseract.exe
  ```

  *(Change in the code if installed elsewhere.)*

### 🔹 Install Ollama

1. Download & install Ollama → [https://ollama.ai](https://ollama.ai)
2. Pull your desired model (e.g., `phi3`):

   ```bash
   ollama pull phi3
   ```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

Then open your browser →
🌐 **[http://localhost:8501](http://localhost:8501)**

---

## 📂 Project Structure

```
Chatbot-infosys-springboard/
│
├── app.py                # Main Streamlit application
├── README.md             # Project documentation
└── requirements.txt      # List of dependencies
```

---

## 💬 How to Use

1. Type your question in the message box.
2. Or upload an image / PDF → text will be extracted using OCR.
3. The AI (via Ollama) replies contextually.
4. Use sidebar to create new chats or search old ones.

---

## 🧑‍💻 Author

**Abhishek Kumar Singh**
B.Tech CSE @ SRM Institute of Science and Technology
📍 Ranchi, Jharkhand

🔗 [LinkedIn](https://www.linkedin.com/in/abhishek-kumar-singh-a90476337/)
💻 [GitHub](https://github.com/Abhishek9978)

---

## 🪪 License

This project is licensed under the **MIT License** — free to use and modify.

---

⭐ *If you like this project, give it a star on GitHub to support future improvements!* ⭐