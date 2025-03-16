# Movie-Research-Agent
Created a RAG Agent using Tkinter (GUI Framework) and LangChain. It allows users to search information about movies or series using tools like DuckDuckGo search and YouTube search. It generates AI powered responses using Google's Gemini Model ("gemini-2.0-flash")

The agent follows the ReAct framework (hwchase17/react prompt) for reasoning (thinking through queries) and acting (fetching relevant data through tools). For eg, when a user asks about a movie the agent decides whether to use DuckDuckGo search (which gets the basic information like IMDB rating, release date etc) or YouTube search (which gets the trailoer link of the movie/series). The tool results and the AI response are then formatted and displayed in the GUI.
