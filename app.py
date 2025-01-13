import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import mysql.connector  # Added MySQL connector
from flask import Flask, request, jsonify  
from google.cloud import dialogflow_v2 as dialogflow



# Flask app setup for IP restriction 
app = Flask(__name__) 

# Add the list of allowed IPs # new
ALLOWED_IPS = ["127.0.0.1", "192.168.1.10"]  # Add your trusted IPs here # new

# Function to restrict access by IP 
@app.before_request  
def restrict_ip():  
    """Restrict access to only allowed IP addresses."""  # new
    client_ip = request.remote_addr  # new
    if client_ip not in ALLOWED_IPS:  # new
        return jsonify({"error": "Access denied. Your IP is not allowed."}), 403  # new





load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Database connection
mydb = mysql.connector.connect(
    host="localhost",       # Host, usually localhost
    user="root",            # Replace with your MySQL username
    password="root",  # Replace with your MySQL password
    database="2chatpdf_db"     # Name of your database
)
if mydb.is_connected():
    print("Successfully connected to the database")
else:
    print("Failed to connect to the database")



mycursor = mydb.cursor()    # To execute queries

# Create a table if not exists (You can adjust the structure as per your need)
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS user_queries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_query TEXT,
        bot_response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Preprocess text chunks (optional: remove punctuations, convert to lowercase)


    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                                  temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain







def query_dialogflow(project_id, session_id, texts, language_code="en"):  
    session_client = dialogflow.SessionsClient()  
    session = session_client.session_path(project_id, session_id)  
    for text in texts:  
        text_input = dialogflow.TextInput(text=text, language_code=language_code)  
        query_input = dialogflow.QueryInput(text=text_input)  
        response = session_client.detect_intent(request={"session": session, "query_input": query_input}) 
        return response.query_result.fulfillment_text  

def query_github(query):
    import requests
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    url = f"https://api.github.com/search/repositories?q={query}"
    response = requests.get(url, headers=headers)
    print(f"GitHub API Status Code: {response.status_code}")  # Debugging line
    if response.status_code == 200:
        results = response.json()["items"][:5]
        return "\n".join([f"{repo['name']}: {repo['html_url']}" for repo in results])
    print(f"GitHub API Error: {response.json()}")  # Debugging line
    return "No repositories found or an error occurred."





def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )

    bot_response = response["output_text"]

    if "answer is not available in the context" in bot_response:  
        # Dialogflow fallback
        project_id = "askyourbook"  # Replace with your project ID
        session_id = "12345"  # Example session ID 
        bot_response = query_dialogflow(project_id, session_id, [user_question])  
        if not bot_response or bot_response.strip() == "answer is not available in the context":
            bot_response = query_github(user_question)  # Query GitHub if no Dialogflow response #***#***#******#*****#*****#*****#





    # Store query and response in the database
    mycursor.execute("""
        INSERT INTO user_queries (user_query, bot_response)
        VALUES (%s, %s)
    """, (user_question, bot_response))

    mydb.commit()  # Commit the changes to the database

    # Output to Streamlit
    st.write("Reply: ", bot_response)

def show_previous_queries():
    mycursor.execute("SELECT * FROM user_queries ORDER BY timestamp DESC LIMIT 5")
    queries = mycursor.fetchall()
    
    for query in queries:
        st.write(f"User Query: {query[1]}")
        st.write(f"Bot Response: {query[2]}")
        st.write(f"Timestamp: {query[3]}")
        st.write("---")


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def save_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        print(f"File successfully saved at: {file_path}")  # Debugging statement
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")  # Error handling
        return None


def main():
    st.set_page_config("Chat PDF")
    st.header("Ace Your Exams🧑🏻‍🎓Ask Your Book📖")

    user_question = st.text_input("Ask a Question from the PDF Files")

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        # new--------------#new: Save the uploaded file to disk and process
        if pdf_docs:
            for pdf_doc in pdf_docs:
                file_path = save_uploaded_file(pdf_doc)  # Save the uploaded file
                st.write(f"File saved at: {file_path}")  # Display the file path
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")

        # Display previous queries for debugging/testing
        st.title("Previous Queries")
        show_previous_queries()

if __name__ == "__main__":
    main()
