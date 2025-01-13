# Chat PDF - Ask Your Book

## Overview
The Chat PDF - Ask Your Book application uploads a PDF file. That PDF gets processed to be able to ask questions about its content. The advanced AI models use MySQL to store user queries, and the web server uses Flask.

Features
Uploading PDFs for content extraction
Question based on content from uploaded PDFs
Previously asked questions and answers
IP access control, rate limiting

Technologies
Python: This is the language used for writing the application
Streamlit: The frontend of the app
Flask: Used to handle the backend file uploads, API requests, etc.
Langchain: For the Natural Language Processing, Conversational AI.
MySQL: Database to store user queries and bot responses.
Google Generative AI: For embeddings and generative AI-based question answering.

Installation
Prerequisites
Before you run the app, make sure you have the following installed:
- Python 3.x
- MySQL (or a MySQL instance running locally)
- Google API credentials for generative AI (stored in a `.env` file)
  
Steps to Set Up

1. Clone the repository
   ```bash
git clone https://github.com/yourusername/ChatBot-AskYourBook.git
   cd ChatBot-AskYourBook
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your `.env` file:
Create a `.env` file in the root directory of your project, and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```

5. Setup MySQL:
   - Make sure you have MySQL installed and running.
   - Update the connection details in the code as needed (in `app.py`).
Run SQL queries to create the database and table to hold user queries:
     ```sql
     CREATE DATABASE IF NOT EXISTS 2chatpdf_db;
     USE 2chatpdf_db;

     CREATE TABLE IF NOT EXISTS user_queries (
         id INT AUTO_INCREMENT PRIMARY KEY,
user_query TEXT,
         bot_response TEXT,
         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );
     ```
     
6. Run the app:
   ```bash
   streamlit run app.py

7. In your browser open the URL `http://localhost:8501` to try the app

API Endpoints

/ask (POST)
- Description**: Asking a question via the uploaded content of the PDF.
- Rate Limit: 10 request/min/IP
- Request Body:
```json
  {
    "question": "Your question here"
  }
  ```
- Response:
  ```json
  {
"answer": "The response from the AI model."
  }
  ```

`/upload` (POST)
- Description: Endpoint to upload PDF files for processing.
- Rate Limit: 5 uploads per minute per IP.
- Form Data: 
  - `file`: The PDF file to upload.
- Response:
  ```json
  {
    "message": "File uploaded successfully.",
    "file_path": "/path/to/uploaded/file"
  }
  ```

License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

 Acknowledgements
- Langchain for its tools and integrations for NLP tasks.
- Google Generative AI for powerful embeddings and AI models.
- Flask and Streamlit for providing a simple way to build web applications.
```
 Key Sections:
1. Overview: Describes the app's functionality.
2. Technologies Used: Lists the main libraries and tools used in the project.
3. Installation: Step-by-step guide on how to install the app on your local machine.
4. API Endpoints: Description of the available API endpoints.
5. License and Acknowledgements: The MIT License, and credits for external libraries.
