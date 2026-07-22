import streamlit as st
import traceback

st.set_page_config(page_title="Research Assistant", page_icon="🔎")
st.title("🔎 Research Assistant")

try:
    from dotenv import load_dotenv
    from pydantic import BaseModel
    from langchain_google_genai import ChatGoogleGenerativeAI
    import os
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
    from tools import search_tool, wiki_tool, save_tool

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)

    class ResearchResult(BaseModel):
        topic: str
        summary: str
        source: list[str]
        tools_used: list[str]

    parser = PydanticOutputParser(pydantic_object=ResearchResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use necessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    tools = [search_tool, wiki_tool, save_tool]
    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    st.success("App initialized successfully!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    query = st.chat_input("What can I help you research?")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                raw_response = agent_executor.invoke({"query": query})
                try:
                    output = raw_response.get("output")
                    if isinstance(output, list):
                        output = output[0].get("text", "")
                    structured_response = parser.parse(output)
                    answer = f"**Topic:** {structured_response.topic}\n\n**Summary:** {structured_response.summary}"
                except Exception as e:
                    answer = f"Error parsing response: {e}\n\nRaw: {raw_response}"

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

except Exception as e:
    st.error("Something failed during setup:")
    st.code(traceback.format_exc())
