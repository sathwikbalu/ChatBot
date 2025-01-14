from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

import os

# Know more about RAG technology in 00-simple-local-rag.ipynb

# Configure Google Generative AI
GOOGLE_API_KEY = 'AIzaSyBWG53DzCscQUFgUhYp1Nufa3tw9NfsfmA'
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS to allow requests from the React frontend
CORS(app)

# Path to the folder containing the .txt files
# Ddata of 4 different documentations in different text files 
folder_path = "./data"

# Use DirectoryLoader with a custom TextLoader specifying the encoding
loader = DirectoryLoader(
    folder_path,
    glob="*.txt",
    loader_cls=lambda path: TextLoader(path, encoding="utf-8")
)

# Load and split the documents
data = loader.load_and_split()

# Ensure there are enough documents and print content for debugging
if len(data) > 1:
    print(data[1].page_content)
    print(f"Total documents loaded: {len(data)}")
else:
    print("Less than 2 documents loaded.")

# Split the text into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
content = "\n\n".join(str(page.page_content) for page in data)
texts = text_splitter.split_text(content)
print(f"Total text chunks: {len(texts)}")

# Generate embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

# Create a Chroma vector store retriever
vector_store = Chroma.from_texts(texts, embeddings).as_retriever()

# Define the prompt template
prompt_template = """
  Please answer the question in as much detail as possible based on the provided context.
  Ensure to include all relevant details. If the answer is not available in the provided context,
  kindly respond with "The answer is not available in the context." Please avoid providing incorrect answers.
\n\n
  Context:\n {context}\n
  Question:\n{question}\n

  Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Configure the Google Generative AI chat model
model = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.3,
    google_api_key=GOOGLE_API_KEY
)

# Create a QA chain
chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Parse the incoming JSON request
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"response": "Please provide a valid message."}), 400

        # Get relevant documents from the vector store
        docs = vector_store.get_relevant_documents(user_message)

        # Generate the response using the QA chain
        response = chain({"input_documents": docs, "question": user_message}, return_only_outputs=True)

        # Return the AI response
        return jsonify({"response": response['output_text']}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "An error occurred processing your request."}), 500


if __name__ == '__main__':
    # Run the server on port 7000
    print("Flask app running")
    app.run(host='0.0.0.0', port=7000, debug=True)
