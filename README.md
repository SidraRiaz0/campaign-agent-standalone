# Campaign Performance Agent - Standalone

AI-powered campaign strategy and ROI prediction tool. Get personalized recommendations before spending ad dollars.

## 🚀 Features

- **Campaign Strategy Generation** - AI analyzes your goals and predicts performance
- **Budget Optimization** - Optimal platform allocation (Meta, LinkedIn, Google)
- **Performance Predictions** - ROAS, CPA, CTR, leads before launch
- **Brand Knowledge Upload** - Train AI on your brand voice with PDF uploads
- **RAG-Powered** - Semantic search with 186+ marketing best practices

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI:** Google Gemini 2.0 Flash
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Database:** Supabase (PostgreSQL + pgvector)
- **Vector Search:** Cosine similarity with pgvector

## 📦 Installation
```bash
# Clone repository
git clone [your-repo-url]
cd campaign-agent-standalone

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure secrets
# Create .streamlit/secrets.toml with:
# [supabase]
# url = "your_supabase_url"
# anon_key = "your_anon_key"
# [gemini]
# api_key = "your_gemini_key"

# Run app
streamlit run main.py
```

## 🎯 Usage

1. **Describe Campaign Goal** - Enter your objective, target audience, KPIs
2. **Set Parameters** - Budget, duration, industry
3. **Upload Brand Docs (Optional)** - PDFs with brand guidelines, past campaigns
4. **Generate Strategy** - AI creates personalized recommendations

## 📊 What You Get

- Budget allocation across platforms
- Predicted leads, CPA, ROAS, CTR
- Optimization tactics
- Risk factors
- Campaign timeline

## 🔐 Configuration

Required secrets in `.streamlit/secrets.toml`:
```toml
[supabase]
url = "your_supabase_project_url"
anon_key = "your_supabase_anon_key"

[gemini]
api_key = "your_google_gemini_api_key"
```

## 🗂️ Project Structure
```
campaign-agent-standalone/
├── main.py                  # Streamlit landing page
├── campaign_agent.py        # Campaign analysis logic
├── brand_rag.py            # RAG system with embeddings
├── supabase_client.py      # Database connection
├── requirements.txt        # Dependencies
└── .streamlit/
    └── secrets.toml        # API keys (gitignored)
```

## 🧪 Key Features

### Campaign Agent
- Analyzes goals with Gemini 2.0 Flash
- Predicts performance metrics
- Recommends platform mix
- Generates optimization strategies

### Brand RAG System
- Uploads PDFs (brand guidelines, past campaigns)
- Chunks text (~500 chars)
- Creates 384-dim embeddings
- Stores in Supabase with pgvector
- Semantic search for personalized recommendations

## 📝 License

[Your License]

## 👥 Contributors

- Your Team

---

**Built with ❤️ using AI**
