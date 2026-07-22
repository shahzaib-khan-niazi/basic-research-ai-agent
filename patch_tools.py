with open("tools.py", "r") as f:
    content = f.read()

old = """from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper"""

new = """from langchain_community.tools import DuckDuckGoSearchRun
import wikipediaapi"""

content = content.replace(old, new)

old_wiki = """api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)"""

new_wiki = """def search_wikipedia(query: str) -> str:
    wiki = wikipediaapi.Wikipedia(user_agent="ResearchAgent/1.0", language="en")
    page = wiki.page(query)
    if page.exists():
        return page.summary[:1000]
    return "No Wikipedia page found for " + query

wiki_tool = Tool(
    name="wikipedia",
    func=search_wikipedia,
    description="Search Wikipedia for information about a topic",
)"""

content = content.replace(old_wiki, new_wiki)

with open("tools.py", "w") as f:
    f.write(content)

print("updated")
