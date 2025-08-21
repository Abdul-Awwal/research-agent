#load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
# import google generative AI
from langchain_google_genai import ChatGoogleGenerativeAI
# import the agent related components(serpapi)
from langchain.agents import load_tools, initialize_agent, AgentType
#Initialize the Google Generative AI model and make the temperature 0 to make the output factual, the higher the temperature the more likely it is to hallucinate
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# "serpapi" is our search tool.
# "llm-math" is a tool that lets the agent use the LLM to do math.
tools = load_tools(["serpapi", "llm-math"], llm=llm)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)


# Define the research query for the agent
query = input("Enter your research query: ")
# Run the agent with the query
print(f"Running agent with query: '{query}'")
agent.run(query)