# Contributing to Student Notes Chatbot

Thanks for contributing! 🎉

## How to Contribute

### Report a Bug
1. Check [existing issues](../../issues)
2. Open a [new issue](../../issues/new) with details:
   - What you did
   - What happened
   - What you expected

### Suggest a Feature
1. Open a [new issue](../../issues/new)
2. Describe the feature and why it would be useful

### Submit Code Changes

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature`
3. **Make changes** following [PEP 8](https://pep8.org/)
4. **Commit**: `git commit -m "Add feature description"`
5. **Push**: `git push origin feature/your-feature`
6. **Open a Pull Request** with description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/student-notes-chatbot.git
cd student-notes-chatbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your Gemini API key to .env

# Run the app
streamlit run app.py
```

## Code Style
- Follow [PEP 8](https://pep8.org/)
- Use descriptive variable names
- Add docstrings to functions
- No hardcoded secrets

## Project Structure
```
├── app.py                 # Streamlit UI
├── rag_pipeline.py        # RAG logic
├── requirements.txt       # Dependencies
├── README.md             # Documentation
└── .github/              # GitHub templates
```

---

**Thank you for contributing!** ✨
