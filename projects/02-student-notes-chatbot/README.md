# 📚 Student Notes Chatbot - AI-Powered Study Assistant

A smart **AI chatbot** that helps students learn effectively by asking questions directly from their course notes using **Retrieval-Augmented Generation (RAG)**.

## ✨ Features

✅ **Upload & Index PDFs** - Upload your course notes, textbooks, or lecture slides  
✅ **Smart Q&A** - Ask questions and get answers grounded in YOUR notes  
✅ **Auto-Generate Study Materials** - Get important questions, topics, and definitions  
✅ **Persistent Chat History** - Continue learning where you left off  
✅ **100% Free** - Uses Gemini free tier (no credit card needed)  
✅ **Local-First** - All embeddings and vector store stored locally  

## 🎯 Use Cases

- 🎓 **Students**: Generate study guides, practice questions, and exam prep materials
- 👨‍🏫 **Teachers**: Create interactive learning tools for your courses
- 📖 **Researchers**: Extract knowledge from PDF documents
- 💼 **Professionals**: Learn from technical documentation and training materials

## 🚀 Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Google Gemini 2.0 Flash Lite (Free) |
| **RAG Framework** | LangChain |
| **Vector Store** | FAISS (Local) |
| **Embeddings** | HuggingFace Sentence-Transformers |
| **Frontend** | Streamlit |
| **PDF Extraction** | PyMuPDF |

## 📦 Requirements

- Python 3.10+
- pip (Python package manager)
- ~2GB disk space for dependencies

## ⚙️ Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/student-notes-chatbot.git
cd student-notes-chatbot
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Get Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Create API key"**
3. Copy your API key

### Step 5: Create Configuration File
Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
USE_LOCAL_PROVIDER=false
GEMINI_MODEL=gemini-2.0-flash-lite
```

### Step 6: Run the Application
```bash
# Windows
$env:USE_LOCAL_PROVIDER="false"
streamlit run app.py

# macOS/Linux
export USE_LOCAL_PROVIDER=false
streamlit run app.py
```

The app will open at **http://localhost:8501**

## 🎓 How to Use

### Upload Notes
1. Go to the **"Upload & Process PDF Notes"** section
2. Select one or more PDF files containing your course material
3. Click **"Process Notes"** to index them
4. Wait for the status to show "🟢 Chatbot is Ready"

### Ask Questions
1. Type any question about your notes in the chat input
2. The chatbot searches your notes and provides answers
3. Sources from your PDFs are displayed below each answer

### Generate Study Materials
1. Click **"📋 Show Important Questions & Topics"** button
2. Get auto-generated:
   - **❓ 5 Important exam questions**
   - **📚 10 Key topics to study**
   - **🔑 5 Key definitions with terms**

## 🏗️ Project Structure

```
student-notes-chatbot/
├── app.py                 # Streamlit UI
├── rag_pipeline.py        # RAG logic & LLM integration
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (API keys)
├── .gitignore            # Git ignore file
├── README.md             # This file
├── faiss_index/          # Vector store (created on first use)
└── sample_notes.pdf      # Example PDF for testing
```

## 🔧 How It Works

```
📄 PDF Upload
    ↓
📑 Text Extraction (PyMuPDF)
    ↓
✂️ Chunking (2000 chars per chunk)
    ↓
🔢 Embeddings (HuggingFace)
    ↓
📦 FAISS Vector Store (Local)
    ↓
User Question
    ↓
🔍 Semantic Search
    ↓
🤖 Gemini AI (with context)
    ↓
💬 Intelligent Answer
```

## ⚠️ Troubleshooting

### API Key Issues
- Make sure `.env` file exists with your Gemini API key
- Verify the key is correct from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 429 Quota Error
- Gemini free tier has rate limits
- Solution: Enable billing in [Google Cloud Console](https://console.cloud.google.com/)
- Or wait a few hours for the free-tier limit to reset

### FAISS Index Errors
- Delete the `faiss_index/` folder
- Reupload your PDFs to rebuild the index

### Streamlit Not Starting
```bash
# Clear Streamlit cache
streamlit cache clear

# Then run again
streamlit run app.py
```

## 🚀 Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and connect your GitHub repo
4. Set secrets in deployment settings:
   ```
   GOOGLE_API_KEY = your_key_here
   USE_LOCAL_PROVIDER = false
   GEMINI_MODEL = gemini-2.0-flash-lite
   ```

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📧 Support

For issues and questions:
- Open a GitHub issue
- Check existing issues/discussions first
- Provide detailed error messages and steps to reproduce

## 🙏 Acknowledgments

Built with [LangChain](https://langchain.com/), [FAISS](https://github.com/facebookresearch/faiss), [Streamlit](https://streamlit.io/), [Google Gemini](https://ai.google.dev/), and [HuggingFace](https://huggingface.co/).

---

**Made with ❤️ for better learning** | ⭐ Star this repo if it helps!
