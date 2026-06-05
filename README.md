# 🎯 AI/ML Portfolio

A comprehensive collection of production-ready AI/ML projects demonstrating expertise in machine learning, data science, and intelligent systems.

## 📚 Projects

### 1. 📊 Customer Churn Prediction System
**Location:** `projects/01-customer-churn-prediction/`

Multi-industry customer churn prediction using machine learning with Streamlit UI.

**Features:**
- 🏢 Industry-specific models (Telecom, Banking, E-commerce)
- 🎯 Real-time prediction with confidence scores
- 📈 Interactive visualizations (ROC curves, feature importance)
- 📁 Bulk CSV upload for batch predictions
- 💾 Persistent model checkpoints

**Tech Stack:** Python, Scikit-learn, Pandas, Streamlit, Plotly

**Performance:**
- ROC-AUC: 0.78-0.85 (varies by industry)
- Accuracy: 75-82%
- Training samples: 2000+ per industry

**Quick Start:**
```bash
cd projects/01-customer-churn-prediction
pip install -r requirements.txt
python train_model.py --industry telecom
streamlit run app.py
```

---

### 2. 📚 Student Notes Chatbot - AI Study Assistant
**Location:** `projects/02-student-notes-chatbot/`

Smart AI chatbot that helps students learn effectively by asking questions directly from their course notes using **Retrieval-Augmented Generation (RAG)**.

**Features:**
- 📤 Upload & Index PDFs - Upload course notes, textbooks, or lecture slides
- 🤖 Smart Q&A - Ask questions and get answers grounded in YOUR notes
- 📖 Auto-Generate Study Materials - Get important questions, topics, and definitions
- 💬 Persistent Chat History - Continue learning where you left off
- 🆓 100% Free - Uses Gemini free tier (no credit card needed)
- 🏠 Local-First - All embeddings and vector store stored locally

**Tech Stack:** Python, LangChain, FAISS, Google Gemini 2.0 Flash Lite, Streamlit, Sentence-Transformers, PyMuPDF

**Use Cases:**
- 🎓 Students: Generate study guides, practice questions, exam prep materials
- 👨‍🏫 Teachers: Create interactive learning tools for courses
- 📖 Researchers: Extract knowledge from PDF documents
- 💼 Professionals: Learn from technical documentation

**Quick Start:**
```bash
cd projects/02-student-notes-chatbot
pip install -r requirements.txt
cp .env.example .env
# Add your Gemini API key to .env (get it from https://aistudio.google.com/app/apikey)
streamlit run app.py
```

**Setup Instructions:**
1. Get free Gemini API key: https://aistudio.google.com/app/apikey
2. Copy `.env.example` to `.env` and add your key
3. Upload PDF files through the app interface
4. Start asking questions!

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git

### Setup

**Clone the repository:**
```bash
git clone https://github.com/Yash7972k/Yash-AI-ML-Portfolio.git
cd Yash-AI-ML-Portfolio
```

**Navigate to a project:**
```bash
cd projects/01-customer-churn-prediction
pip install -r requirements.txt
```

---

## 📂 Repository Structure

```
Yash-AI-ML-Portfolio/
├── projects/
│   ├── 01-customer-churn-prediction/    ⭐ Machine Learning
│   ├── 02-student-notes-chatbot/        ⭐ RAG & AI
│   └── 03-future-project/
├── README.md                             (this file)
├── LICENSE
└── .gitignore
```

Each project includes:
- ✅ Source code (`app.py`, `train_model.py`, etc.)
- ✅ Dependencies (`requirements.txt`)
- ✅ Documentation (`README.md`)
- ✅ Production-ready configuration
- ✅ Test scripts (where applicable)

---

## 🎓 Skills Demonstrated

- **Machine Learning:** Classification, Feature Engineering, Model Evaluation
- **Data Processing:** Pandas, NumPy, Data Cleaning, Preprocessing
- **AI/LLM:** RAG (Retrieval-Augmented Generation), Vector Embeddings, FAISS, Prompt Engineering
- **Web Frameworks:** Streamlit, Flask, Django
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Vector Search:** FAISS, Semantic Search, Embeddings
- **Best Practices:** Clean code, documentation, version control
- **Production:** Model persistence, error handling, scalability

---

## 📈 Project Status

| Project | Status | Last Updated |
|---------|--------|--------------|
| 01-customer-churn-prediction | ✅ Active | 2026-06-05 |
| 02-student-notes-chatbot | ✅ Active | 2026-06-05 |
| 03-... | 📋 Planned | - |

---

## 🔧 Development

### Add a New Project

1. Create a new directory:
   ```bash
   mkdir projects/02-your-project-name
   ```

2. Include these files:
   - `app.py` or `main.py` (entry point)
   - `requirements.txt` (dependencies)
   - `README.md` (project documentation)
   - `LICENSE` (MIT recommended)

3. Update the main README with project details

4. Commit and push:
   ```bash
   git add .
   git commit -m "feat: Add new project - Your Project Name"
   git push origin main
   ```

---

## 📋 Project Ideas (Planned)

- [ ] Time Series Forecasting (Stock Price Prediction)
- [ ] NLP (Sentiment Analysis, Text Classification)
- [ ] Computer Vision (Image Classification, Object Detection)
- [ ] Recommendation System (Collaborative Filtering)
- [ ] Anomaly Detection (Fraud Detection)
- [ ] Reinforcement Learning (Game AI)

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Commit: `git commit -m "feat: Add new feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📝 License

This portfolio is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 📧 Contact & Links

- **GitHub:** [Yash7972k](https://github.com/Yash7972k)
- **Email:** [Your Email]
- **LinkedIn:** [Your LinkedIn]
- **Portfolio:** [This Repository]

---

## 🎯 Learning Path

**For Beginners:**
1. Start with 01-customer-churn-prediction
2. Understand data preprocessing and feature engineering
3. Learn model training and evaluation

**For Intermediate:**
1. Explore different ML algorithms
2. Analyze model performance metrics
3. Implement custom preprocessing pipelines

**For Advanced:**
1. Optimize models for production
2. Implement automated pipelines
3. Deploy models as APIs

---

## 📚 Resources

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Streamlit Documentation](https://streamlit.io/)
- [Machine Learning Best Practices](https://ml-ops.systems/)

---

**Last Updated:** 2026-06-05  
**Repository:** https://github.com/Yash7972k/Yash-AI-ML-Portfolio  
**Status:** 🟢 Active & Maintained
