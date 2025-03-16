import tkinter as tk
from tkinter import scrolledtext
from langchain_community.tools import DuckDuckGoSearchRun
from youtube_search import YoutubeSearch
from langchain import hub
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.base import BaseCallbackHandler
import os
from dotenv import load_dotenv

# Function to get YouTube Trailer Link
def youtube_link(movie_name):
    """Search YouTube for the official trailer and return the first link."""
    results = YoutubeSearch(movie_name + " official trailer", max_results=1).to_dict()
    
    if results:
        video_id = results[0]['id']
        trailer_url = f"https://www.youtube.com/watch?v={video_id}"
        return f"🎬 Found trailer: {trailer_url}"
    else:
        return "No trailer found."

class TkinterCallbackHandler(BaseCallbackHandler):
    def __init__(self, chat_window):
        self.chat_window = chat_window
        self.tool_output_printed = False  

    def on_agent_action(self, action, **kwargs):
        tool_name = action.tool 
        tool_input = action.tool_input
        formatted_message = f"\n Calling {tool_name}: \"{tool_input}\"\n\n"
        self.log(formatted_message, "tool_call")
        self.tool_output_printed = False

    def on_tool_end(self, output, **kwargs):
        if not self.tool_output_printed:
            formatted_message = f"RESULTS: {output}\n\n"
            self.log(formatted_message,"result")
            self.tool_output_printed = True

    def log(self, message, tag=""):
        self.chat_window.insert(tk.END, message + "\n", tag)
        self.chat_window.yview(tk.END)
        self.chat_window.update_idletasks()

# Function to create and configure the ReAct Agent
def create_agent():
    load_dotenv()
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=os.getenv('GEMINI_API_KEY'))
    
    search = DuckDuckGoSearchRun() 
    duckduckgo_tool = Tool(
        name='DuckDuckGo Search',
        func=search.run,
        description='Search for movies/series to extract basic information (IMDB rating, release date, director, starring)'
    )

    youtube_tool = Tool(
        name="YouTube Search",
        func=youtube_link,
        description="Find a YouTube trailer link for a movie or series."
    )

    tools = [duckduckgo_tool, youtube_tool]
    
    prompt = hub.pull('hwchase17/react')
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor

# Function to handle search and agent execution
def search_movie():
    query = entry.get()
    if not query:
        return

    chat_history.insert(tk.END, f"\n👤 {query}\n\n", "user")
    chat_history.update_idletasks()

    callback_handler = TkinterCallbackHandler(chat_history)

    try:
        response = agent_executor.invoke({"input": query}, {"callbacks": [callback_handler]})
        response_text = response.get("output", "No response received.")
    except Exception as e:
        response_text = f"Error: {str(e)}"

    chat_history.insert(tk.END, f"\n🤖 {response_text}\n ", "ai")
    chat_history.yview(tk.END)

# Function to create the GUI
def create_gui():
    global root, entry, search_button, chat_history, agent_executor

    root = tk.Tk()
    root.title("Movie Research Assistant")
    root.geometry("700x500")
    root.configure(bg="#EAEAEA")

    # Top bar
    header = tk.Frame(root, bg="#1976D2", height=30)
    header.pack(fill="x")

    title_label = tk.Label(header, text="Movie Research Assistant", fg="white", bg="#1976D2", font=("Arial", 12, "bold"))
    title_label.pack(pady=5)

    # Chat history
    chat_history = scrolledtext.ScrolledText(root, width=75, height=20, wrap=tk.WORD, bg="white", fg="black", font=("Arial", 10))
    chat_history.pack(padx=10, pady=10, fill="both", expand=True)

    # Styling for messages
    chat_history.tag_config("user", foreground="green", font=("Arial", 12, "bold"))
    chat_history.tag_config("ai", foreground="black", font=("Arial", 12, "bold"))
    chat_history.tag_config("tool_call", background="#FFFFC5", font=("Arial", 10, "italic", "bold"))
    chat_history.tag_config("result", background="#CBC3E3", font=("Arial", 10, "bold"))
    chat_history.tag_config("trailer_link", foreground="blue", underline=True)

    # Input frame
    input_frame = tk.Frame(root, bg="#EAEAEA")
    input_frame.pack(fill="x", padx=10, pady=5)

    entry = tk.Entry(input_frame, width=60, font=("Arial", 12), bg="white", fg="black", relief=tk.GROOVE, bd=2)
    entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

    search_button = tk.Button(input_frame, text="Send", font=("Arial", 12, "bold"), bg="#1976D2", fg="white", relief=tk.FLAT, command=search_movie)
    search_button.pack(side="right", padx=5, pady=5)

    agent_executor = create_agent()
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
