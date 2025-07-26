# 📧 Intelligent Email Context Assistant 🤖

This project is an AI-powered email assistant built using **Django** and **Groq API (LLaMA3)** that connects to your Gmail inbox, intelligently understands user queries using LLMs, and filters and summarises your emails accordingly — all in a beautiful, context-aware HTML output.

---

## 🚀 Features

- ✅ **Gmail IMAP Integration** – Securely connect to Gmail and retrieve recent emails
- 🧠 **LLM-Powered Intent Understanding** – Uses Groq's LLaMA 3 to analyze user queries
- 🧹 **Smart Email Filtering** – Filters relevant emails based on user intent using AI
- 🧾 **Summarized and Structured Replies** – Clean and readable HTML format response
- 🔄 **Concurrent Processing** – Email fetch and intent analysis happen in parallel
- 🌐 **Django Web Interface** – Easily interact with the assistant via browser

---

## 🛠️ Tech Stack

| Tool / Framework     | Purpose                                         |
|----------------------|--------------------------------------------------|
| **Python 3.10+**      | Core programming language                       |
| **Django**            | Web framework to serve frontend & backend       |
| **IMAPLIB**           | For Gmail access via IMAP                       |
| **email / decode_header** | Parsing and decoding email content         |
| **Groq API (LLaMA3)** | Language model for intent analysis and filtering|
| **ThreadPoolExecutor**| Concurrent execution of email fetching and AI   |
| **HTML**              | Email results are returned in formatted HTML    |

---

## 🧠 How It Works

1. **User enters a natural language query** (e.g., *“show me emails from John last week”*)
2. **LLM interprets the intent**
   - Example intent: *“Find emails from sender: John within the past 7 days”*
3. **Email content is fetched** from Gmail inbox
4. **Groq's LLM filters emails** using the intent and generates a structured HTML summary
5. **Results are summarised and displayed** on console or web interface

---

## 🖥️ Running Locally (Web Interface with Django)

### 1. **Clone the repository**

```bash
git clone https://github.com/anchor369/Hackathon_AI_LLM.git
