# 🦅 NEXORA AI — Your Intelligent Study Companion

NEXORA AI is an AI-powered chatbot and study assistant built with Python and Streamlit. It uses the Groq API to generate intelligent responses and Retrieval-Augmented Generation (RAG) to answer questions from your own documents.

Whether you want to ask general questions, understand difficult topics, summarize information, or chat with your PDF and Word documents, NEXORA AI makes learning easier.

---

## ✨ Features

### 💬 1. AI Chat

- Ask questions and receive AI-generated answers.
- Get explanations in simple and understandable language.
- Ask programming, educational, and general questions.
- Generate summaries and practice questions.
- Continue conversations with chat context.

### 📚 2. Chat With Your Documents (RAG)

Upload your own documents and ask questions about their content.

**Supported formats:**
- PDF (`.pdf`)
- Word (`.docx`)
- Text (`.txt`)
- Markdown (`.md`)

**Features include:**
- Automatic document text extraction.
- Smart text chunking with overlapping sections.
- Semantic search using embeddings.
- Answers based on relevant document content.
- Source filename and page references when available.
- Persistent document storage.

### 🗂️ 3. Unified Chat History

- Normal Chat and Document Chat are saved in one Chat History.
- Reopen previous conversations.
- Start a fresh conversation whenever you want.
- Start multiple separate conversations with the same saved document.
- Document Chat remembers its selected document.

### 📁 4. Saved Documents

- Upload and process documents.
- View previously uploaded documents.
- Reuse saved documents without uploading them again.
- Delete documents when they are no longer needed.

### 🎨 5. Modern User Interface

- Professional dark-themed interface.
- Animated NEXORA AI branding.
- Interactive sidebar.
- Organized chat layout.
- Copy AI answers easily.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application interface |
| Groq API | AI response generation |
| OpenAI Python SDK | API communication |
| ChromaDB | Persistent vector database |
| Sentence Transformers | Text embeddings |
| Hugging Face | Embedding model |
| PyPDF | PDF text extraction |
| python-docx | Word document extraction |
| python-dotenv | Environment configuration |
| JSON | Conversation history storage |

---

## 📂 Project Structure

```text
NEXORA-AI/
│
├── App.py
├── AI_Client.py
├── Rag.py
├── .env
│
├── documents/
├── vector_db/
└── chat_history.json
```

### File Description

| File | Description |
|---|---|
| `App.py` | Main Streamlit application. Handles the interface, chat, document uploads, and conversation history. |
| `AI_Client.py` | Connects the application to Groq and generates AI responses. |
| `Rag.py` | Handles document extraction, text chunking, embeddings, semantic search, and ChromaDB storage. |
| `.env` | Stores the private Groq API key and model configuration. |
| `documents/` | Stores uploaded original documents. |
| `vector_db/` | Stores document embeddings and metadata. |
| `chat_history.json` | Stores saved conversations. |

**Note:** The `documents/`, `vector_db/`, and `chat_history.json` files are created automatically when needed.

---

## 🚀 Installation & Setup

Follow these steps to install and run NEXORA AI on your computer.

### Step 1: Install Python

First, install Python on your computer.

1. Visit https://www.python.org/downloads/
2. Download Python.
3. Run the installer.
4. On Windows, select **Add Python to PATH** if the option is available.
5. Complete the installation.

To check Python installation, open Command Prompt or Terminal and type:

```bash
python --version
```

If Windows does not recognize `python`, try:

```bash
py --version
```

### Step 2: Download NEXORA AI

1. Open this GitHub repository.
2. Click the green **Code** button.
3. Select **Download ZIP**.
4. Extract the downloaded ZIP file.
5. Open the extracted NEXORA AI project folder.

Make sure `App.py`, `AI_Client.py`, and `Rag.py` are together in the same folder.

### Step 3: Open the Project in VS Code

1. Install Visual Studio Code if you do not already have it.
2. Open VS Code.
3. Select **File → Open Folder**.
4. Select your NEXORA AI project folder.
5. Open **Terminal → New Terminal**.

You can also open Command Prompt directly inside the project folder.

### Step 4: Create a Groq API Key

NEXORA AI uses Groq to generate AI responses.

1. Visit https://console.groq.com/
2. Create an account or sign in.
3. Open the API Keys section.
4. Create a new API key.
5. Copy the key and keep it private.

### Step 5: Create the `.env` File

Inside your project folder:

1. Create a new file.
2. Name it exactly `.env`.
3. Open the file.
4. Add the following configuration:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Replace `your_groq_api_key_here` with your actual Groq API key.

Save the file.

**Important:** Never share your API key or upload your `.env` file to GitHub.

The model setting is optional. If omitted, NEXORA AI uses `openai/gpt-oss-20b` by default.

### Step 6: Install Required Libraries

Open the VS Code terminal inside your project folder.

First, update pip:

```bash
python -m pip install --upgrade pip
```

Now install all required packages:

```bash
python -m pip install streamlit openai python-dotenv chromadb pypdf sentence-transformers python-docx
```

If you are using Windows and `python` does not work, use `py`:

```bash
py -m pip install streamlit openai python-dotenv chromadb pypdf sentence-transformers python-docx
```

Wait until all packages are installed.

### Step 7: Run NEXORA AI

In the same terminal, execute:

```bash
python -m streamlit run App.py
```

On Windows, you can also use:

```bash
py -m streamlit run App.py
```

Streamlit will start the application and usually open it automatically in your browser.

If it does not open, visit:

http://localhost:8501

🎉 Congratulations! NEXORA AI is now running on your computer.

Keep the terminal open while using the application.

---

## 📖 How to Use NEXORA AI

### 1. Start a Normal Conversation

1. Open NEXORA AI in your browser.
2. Find the chat input at the bottom.
3. Type your question.
4. Press Enter.
5. NEXORA AI will generate an answer.

**Example:**

`What is Artificial Intelligence?`

You can ask questions about programming, education, technology, and many other topics.

Normal Chat does not search uploaded documents.

### 2. Upload Your Document

1. Open the sidebar.
2. Find the Knowledge Base section.
3. Click the document upload option.
4. Select your PDF, DOCX, TXT, or MD file.
5. Click **Process Documents**.
6. Wait until processing is completed.

Your document will appear in Saved Documents.

**First-time processing:** NEXORA AI may need to download its embedding model. This can take some time depending on your internet connection.

### 3. Start a Document Chat

1. Find Saved Documents in the sidebar.
2. Click the document you want to use.
3. Select **Start New Document Chat**.
4. A new conversation will open for that document.
5. Ask questions about its contents.

**Example questions:**
- Summarize this document.
- Explain the important points.
- What is the main topic?
- Create five practice questions from this document.

NEXORA AI searches the selected document for relevant information.

### 4. Start Another Chat With the Same Document

You do not need to upload the same document again.

1. Open Saved Documents.
2. Select the same document.
3. Click **Start New Document Chat**.
4. A completely new Document Chat will begin.

Each conversation is saved separately in the same Chat History.

### 5. Start a New Normal Conversation

Click **New Conversation** in the sidebar.

This will:
- Clear the active document selection.
- Start a fresh conversation.
- Turn off document search.
- Keep your previous conversations in Chat History.

### 6. Reopen Previous Conversations

1. Open Chat History.
2. Select any saved conversation.
3. NEXORA AI will restore its messages.
4. Document conversations restore their associated document selection.

### 7. Delete a Saved Document

1. Open Saved Documents.
2. Expand the document.
3. Click **Delete Document**.
4. Confirm the action if prompted.

The document's stored chunks are removed from the vector database, and its original saved file is deleted.

Deleting a document does not automatically delete old chat messages. However, new searches cannot use a document that has been deleted.

---

## 🧠 How RAG Works in NEXORA AI

RAG stands for **Retrieval-Augmented Generation**.

It allows an AI application to retrieve relevant information from your own documents before generating an answer.

NEXORA AI uses the following process:

1. **Document Upload:** You upload a document.
2. **Text Extraction:** The application extracts readable text.
3. **Text Chunking:** The text is divided into smaller sections.
4. **Embedding Generation:** Sentence Transformers converts text into numerical vectors.
5. **Vector Storage:** ChromaDB stores the vectors and document information.
6. **Semantic Search:** Your question is compared with the stored document sections.
7. **AI Response:** Relevant information is sent to Groq, which generates the answer.
8. **Source References:** Available document filenames and page numbers are included.

**Embedding Model**

`sentence-transformers/all-MiniLM-L6-v2`

**Default Groq Model**

`openai/gpt-oss-20b`

---

## ⚙️ Configuration

You can change the Groq model through the `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

The application uses the following RAG defaults:

| Setting | Default |
|---|---|
| Maximum document size | 25 MB |
| Chunk size | 200 words |
| Chunk overlap | 40 words |
| Search results | 5 |
| Minimum similarity score | 0.25 |
| Embedding model | all-MiniLM-L6-v2 |

These settings are defined in `Rag.py`.

---

## 🛠️ Troubleshooting

### Problem 1: "GROQ_API_KEY is missing"

**Solution:**
- Check whether `.env` exists.
- Make sure it is in the same folder as `AI_Client.py`.
- Check the spelling of `GROQ_API_KEY`.
- Restart NEXORA AI.

### Problem 2: "ModuleNotFoundError"

**Solution:** Install the required libraries again:

```bash
python -m pip install streamlit openai python-dotenv chromadb pypdf sentence-transformers python-docx
```

### Problem 3: "This document has already been uploaded"

**Reason:** The same document content is already stored.

**Solution:** Open Saved Documents and start a new Document Chat using the existing document.

### Problem 4: PDF text cannot be extracted

**Reason:** Your PDF may contain scanned pages or images instead of selectable text.

**Solution:** Use a text-based PDF or convert the scanned PDF into a searchable PDF using OCR before uploading.

NEXORA AI does not currently include OCR.

### Problem 5: NEXORA AI is taking a long time to process a document

**Reason:** The embedding model may be downloading or loading for the first time.

**Solution:**
- Keep your internet connection active.
- Wait for the model to finish downloading.
- Avoid closing the application during processing.

### Problem 6: Groq API Error

**Possible reasons:**
- Incorrect API key.
- Model unavailable to your account.
- Internet connection problem.
- API usage limit reached.

**Solution:** Check your Groq API key, selected model, internet connection, and account usage limits.

### Problem 7: Application does not start

Make sure:
- Python is installed.
- Required packages are installed.
- All three Python files are in the same folder.
- You are running the command from the project folder.

Run again:

```bash
python -m streamlit run App.py
```

---

## 🔐 Privacy & Security

- Your Groq API key should remain private.
- Never upload `.env` to a public GitHub repository.
- Uploaded original documents and the local vector database are stored on the computer running NEXORA AI.
- When using Document Chat, relevant document text and conversation messages are sent to Groq to generate an answer.
- Do not upload confidential documents unless you have permission to share their contents with the AI service.
- Local chat history and document data may be lost if their files or folders are deleted.

**Recommended `.gitignore`:**

```gitignore
.env
__pycache__/
*.pyc
vector_db/
documents/
chat_history.json
```

---

## 📌 Important Information

- An active Groq API key is required for AI responses.
- An internet connection is required for Groq API access.
- The first embedding-model download requires internet access.
- Supported document formats are PDF, DOCX, TXT, and MD.
- Maximum document size is 25 MB.
- Scanned PDFs require OCR before uploading.
- Chat History and document data are stored locally in the project folder.

---

## 👨‍💻 Author

**Muhammad Musab**

**Project:** NEXORA AI — Your Intelligent Study Companion

---

## ⭐ Support

If you find NEXORA AI useful, consider giving this repository a ⭐ on GitHub.

Feel free to explore, learn, and build with it.

**Ask. Learn. Understand. Grow.**

🐺 **NEXORA AI**
