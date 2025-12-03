# Personal AI Knowledge Assistant

A **Flask-based AI chatbot** powered by the **OpenAI API**. This app answers user queries with either brief or detailed responses and provides a clean, interactive web interface for real-time AI-powered assistance.



## Features

- **AI-powered responses** using OpenAI API  
- **Brief or detailed answers** based on user preference  
- **Clean, interactive web interface**  
- **Real-time query handling** for instant responses  
- **Built with Flask** for a lightweight web experience  



## How It Works

1. **User Input**:  
   - Type your query into the web interface.  

2. **Query Processing**:  
   - The app sends the query to the OpenAI API and receives a response.  

3. **Response Display**:  
   - The AI-generated answer is displayed instantly in the web interface.  

4. **Optional Detail Mode**:  
   - Users can choose between brief or detailed responses depending on their needs.  



## How to Run

1. **Install Python**  
   - Make sure **Python 3.x** is installed: [python.org](https://www.python.org/downloads/)  

2. **Install Dependencies**  
   - Navigate to the project folder and install required packages:  
     ```bash
     pip install Flask openai
     ```  

3. **Set OpenAI API Key**  
   - Get your OpenAI API key from [OpenAI](https://platform.openai.com/)  
   - Set it as an environment variable:  
     ```bash
     export OPENAI_API_KEY='your_api_key_here'   # For Linux/Mac
     setx OPENAI_API_KEY "your_api_key_here"    # For Windows
     ```  

4. **Run the App**  
   - Start the Flask server:  
     ```bash
     python app.py
     ```  

5. **Open in Browser**  
   - Go to:  
     ```
     http://127.0.0.1:5000/
     ```  
   - Enter your query and get AI-powered responses.  



## Why This Project

- Learn **Flask web development** with an AI integration  
- Practice using the **OpenAI API** in a real-world application  
- Build a **personal AI assistant** for knowledge queries  
- Explore **real-time web-based interactions** with AI  



## Usage

- Type any question in the input field  
- Choose brief or detailed response mode (if available)  
- View AI-generated answers instantly  
- Interact multiple times for follow-up queries  

---
