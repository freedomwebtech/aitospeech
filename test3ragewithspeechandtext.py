import os
from flask import Flask, render_template_string, request, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from groq import Groq

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Groq Client
client = Groq(api_key="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")  # Replace with your actual API key

# Configure Google AI
os.environ["GOOGLE_API_KEY"] = "AIzaSyDmRzJ2NbaaCA2ckK9eb8lAqnhH3AFhfrc"  # Replace with your actual API key

vector_store = None  # Global variable to store FAISS index

# Extract text from PDF
def get_pdf_text(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Split text into smaller chunks
def split_text(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_text(text)

# Embed text and store in FAISS index
def create_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

# Query AI with FAISS search
def handle_query(query):
    global vector_store
    if vector_store is None:
        return "Please upload a PDF first."

    search_results = vector_store.similarity_search(query, k=5)
    context = " ".join([result.page_content for result in search_results])

    prompt = f"Answer the following question based on the provided context: {query}\n\nContext: {context}"

    completion = client.chat.completions.create(
        model="qwen-2.5-32b",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        stream=False,
    )

    return completion.choices[0].message.content.strip()

# HTML Chatbot UI with PDF Upload
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI PDF Chatbot</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f4f4f4;
        }
        .chat-container {
            width: 90%;
            max-width: 600px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        .chat-box {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background: #fff;
            border-radius: 5px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            max-width: 80%;
        }
        .user-message { background: #007BFF; color: white; text-align: right; margin-left: auto; }
        .bot-message { background: #e9ecef; color: black; text-align: left; margin-right: auto; }
        input, button { width: 100%; padding: 10px; margin-top: 10px; border-radius: 5px; border: none; }
        #send { background-color: #007BFF; color: white; }
        #speak { background-color: #28a745; color: white; }
        #listen { background-color: #ffc107; color: black; }
        #clear { background-color: #6c757d; color: white; }
        #upload { background-color: #ff5733; color: white; }
    </style>
</head>
<body>

    <div class="chat-container">
        <h2>PDF AI Chatbot</h2>

        <form id="upload-form" enctype="multipart/form-data">
            <input type="file" id="file-input" required />
            <button type="submit" id="upload">Upload PDF</button>
        </form>

        <div class="chat-box" id="chat-box"></div>
        <input type="text" id="user-input" placeholder="Ask about the PDF..." />
        <button id="send">Send</button>
        <button id="speak" disabled>Speak Response</button>
        <button id="listen">🎤 Speak</button>
        <button id="clear">Clear Chat</button>
    </div>

    <script>
        document.getElementById('upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            let fileInput = document.getElementById('file-input').files[0];
            if (!fileInput) return;

            let formData = new FormData();
            formData.append("file", fileInput);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
            });
        });

        document.getElementById('send').addEventListener('click', () => {
            let userInput = document.getElementById('user-input').value;
            if (userInput.trim() === "") return;

            let chatBox = document.getElementById('chat-box');
            let userMessage = document.createElement("div");
            userMessage.classList.add("message", "user-message");
            userMessage.innerText = userInput;
            chatBox.appendChild(userMessage);
            document.getElementById('user-input').value = "";

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_input: userInput })
            })
            .then(response => response.json())
            .then(data => {
                let botMessage = document.createElement("div");
                botMessage.classList.add("message", "bot-message");
                botMessage.innerText = data.response;
                chatBox.appendChild(botMessage);
                chatBox.scrollTop = chatBox.scrollHeight;
                document.getElementById('speak').disabled = false;
                document.getElementById('speak').dataset.response = data.response;
            });
        });

        document.getElementById('speak').addEventListener('click', () => {
            let text = document.getElementById('speak').dataset.response;
            if (text) {
                puter.ai.txt2speech(text).then(audio => {
                    audio.play();
                });
            }
        });

        // 🔥 Speech Recognition Feature
        document.getElementById('listen').addEventListener('click', () => {
            puter.ai.speech2txt().then(text => {
                document.getElementById('user-input').value = text;
            }).catch(err => {
                console.error("Speech recognition error:", err);
            });
        });

        document.getElementById('clear').addEventListener('click', () => {
            document.getElementById('chat-box').innerHTML = "";
            document.getElementById('speak').disabled = true;
        });
    </script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_code)

@app.route("/upload", methods=["POST"])
def upload():
    global vector_store
    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    pdf_text = get_pdf_text(filepath)
    text_chunks = split_text(pdf_text)
    vector_store = create_vector_store(text_chunks)

    return jsonify({"message": "PDF uploaded and processed successfully!"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    response = handle_query(data.get("user_input", ""))
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=False, port=8081)
