# SyncPoint-AI
# 📝 Enterprise Knowledge Hub: Time-Aware RAG Assistant

> **A professional-grade RAG (Retrieval-Augmented Generation) assistant that bridges the gap between static documents and live corporate knowledge.**

---

## 🚀 The Core Innovation: Solving the "Temporal Gap"
Most RAG systems treat data as static blocks of text. When asked **"Who is presenting next?"**, standard assistants often fail because they lack an internal clock and context of the current date.

**This project solves that by:**
1. **Dynamic Context Injection**: Merging real-time system timestamps into the LLM's prompt window.
2. **Chronological Reasoning**: Engineering specific instructions that force the AI to compare document dates (from Confluence/PDFs) against "Today's Date."
3. **Multi-Source Orchestration**: Seamlessly indexing live Confluence Cloud pages and local PDF assets into a unified ChromaDB vector store.

---

## ✨ Key Features
* **🌐 Live Confluence Sync**: Connect directly to Atlassian Confluence via Page IDs to pull the latest team documentation.
* **📄 PDF Intelligence**: Local document processing with automatic vector indexing.
* **🕒 Temporal Awareness**: Specifically tuned to handle schedules, deadlines, and "upcoming" events.
* **🎨 SaaS-Inspired UI**: A custom-styled Streamlit interface featuring:
    * Categorized Knowledge Base management.
    * Transparent, interactive "hover-state" source deletion.
    * Persistent session history (Save/Load/Delete chats).
* **🧠 Contextual Integrity**: Optimized chunking (1024 tokens) with overlap to ensure names and dates remain linked during retrieval.

---

## 🛠️ Technical Stack
* **Orchestration**: LlamaIndex
* **Vector Database**: ChromaDB
* **Language Models**: OpenAI (GPT-4o) / Gemini 1.5
* **Frontend**: Streamlit
* **Data Sources**: Confluence Cloud API & Local PDF Directory

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

git clone [https://github.com/vipin-nirwal/SyncPoint-AI.git](https://github.com/vipin-nirwal/SyncPoint-AI.git)
cd SyncPoint-AI

### 2. Install Depenedencies

pip install -r requirements.txt

### 3. Configure Environment Variables

Create a .env file in the root and set below properties.

* OPENAI_API_KEY=your_openai_api_key
* CONFLUENCE_URL=[https://your-domain.atlassian.net](https://your-domain.atlassian.net)
* CONFLUENCE_EMAIL=your_email@company.com
* CONFLUENCE_API_TOKEN=your_token_here
* HF_TOKEN=HuggingFace_token #this is not mandatory but there might be some warning if you do not have this

### 4. Launch the Application

streamlit run app.py



