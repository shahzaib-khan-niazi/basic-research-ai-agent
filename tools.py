from langchain_community.tools import DuckDuckGoSearchRun
import wikipediaapi
from langchain_classic.tools import Tool
from datetime import datetime

def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

def search_wikipedia(query: str) -> str:
    wiki = wikipediaapi.Wikipedia(user_agent="ResearchAgent/1.0", language="en")
    page = wiki.page(query)
    if page.exists():
        return page.summary[:1000]
    return "No Wikipedia page found for " + query

wiki_tool = Tool(
    name="wikipedia",
    func=search_wikipedia,
    description="Search Wikipedia for information about a topic",
)
