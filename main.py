import warnings
import os
from crewai_tools import CSVSearchTool
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew
from crewai import LLM
from pydantic import BaseModel, Field
from typing import Type
from discordbot import run_discord_bot
import threading
import time

warnings.filterwarnings('ignore')

os.environ['GOOGLE_API_KEY'] = "AIzaSyAsOcKmk-zh9sPZM5gWprOnmsG4xnIr4x0"


llm = LLM(
    provider="google",
    model="gemini/gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    api_key="AIzaSyAsOcKmk-zh9sPZM5gWprOnmsG4xnIr4x0"
)

# CSV search tool
csvreader = CSVSearchTool(
    file_path='instagram_posts.csv',
    config=dict(
        llm=dict(
            provider="google",
            config=dict(
                model="gemini/gemini-1.5-flash"  # Corrected model name
            ),
        ),
        embedder=dict(
            provider="google",
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # Add any additional parameters if needed
            ),
        ),
    )
)

#Custom tool to search gif
class MyToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    query: str = Field(..., description="The Argument has to be a string and should be keywords to find gif closely related to them")

class GIFSearchTool(BaseTool):
    name: str="GIF Search tool"
    description: str="Search a gif based one provided query"
    args_schema: Type[BaseModel] = MyToolInput
    def _run(self, query:str) ->str:
        """
        Search for a GIF from a vast library of GIFs available on the internet which matches with the provided query
        
        Args:
            query: The GIF you want to search

        Returns:
            A default message whether the gif was successfully installed or not in string
        """
        import requests
        api_key = "vZ7hCK3M3NfHwoTPX9ypgZPucKOhhxVE"
        print("This was the query given as input to the Gif Search tool:", query)
        response = requests.get(
            "https://api.giphy.com/v1/gifs/search",
            params={'api_key': api_key, 'q':query, 'limit':1}
        )
        data = response.json()
        if data["data"]:
            gif_url = data['data'][0]["images"]["original"]["url"]
    
            response = requests.get(gif_url)

            with open("gif.gif", "wb") as f:
                f.write(response.content)
            return "Gif found and saved as gif.gif"
        else:
            return "No GIF found"

giphy_tool = GIFSearchTool()

# Define Agents
content_writer = Agent(
    role="Shower Thought Strategist",
    goal="Create viral-worthy shower thoughts with 'aha' moments",
    backstory="""A creative genius specializing in paradoxical observations 
    and unexpected perspectives. Known for crafting thoughts that spark 
    both contemplation and debate across social media.""",
    allow_delegation=False,
    tools=[csvreader],
    verbose=True,
    llm=llm
)

gif_finder = Agent(
    role="Expert GIF Scraper",
    goal="Find the perfect GIFs for shower thoughts",
    backstory="A creative visual curator who finds matching GIFs for abstract thoughts.",
    tools=[giphy_tool],
    verbose=True,
    llm=llm
)

# Define Tasks
shower_thought_task = Task(
    description= "Analyze the CSV file of previous shower thoughts using the CSVSearchTool. "
        'The provided .csv file contains the following columns: "PostURL","ShowerThought","VideoViews","Likes","Comments","Saves","shares","EngagementRate"'
        "Use the tool to search for top-performing shower thoughts by querying engagement metrics like \"Likes\", \"VideoViews\", or \"EngagementRate\". "
        "query out \"ShowerThought\" with higest \"VideoViews\" and lowest ones as well to check what is working and what is not "
        "Identify patterns in style or structure and create new thoughts inspired by those successful ones. "
        "Avoid repetitive themes and try to generate thoughts with fresh, diverse ideas.",
    
    expected_output="""A thought formatted as:
    [Thought text here]
    
    [Line break]
    [One line caption here]
    -
    -
    -
    -
    -
    #showerthoughts #[relevant_tag1] #[relevant_tag2] #[relevant_tag3]
    eg.
    In 8 more years, we won't have to wonder if the date is written in mm-dd or mm-yy.
    
    I don't overthink. Also me
    -
    -
    -
    -
    -
    #showerthoughts #deepthoughts #randomthoughts #random
    """,
    
    agent=content_writer,
    output_file="draft_thought.md"
)

gif_task = Task(
    description="Find a suitable GIF for the showerthought made by Shower Thought Strategist "
        "using GIFSerachTool. Make sure to provide keywords realted to the gif you are looking for and not a sentence. "
        "always try to use 'confused' keyword in your keywords and make sure not to use more than 3 keywords.",
    agent=gif_finder,
    expected_output="A message confirming that the gif has been saved successfully.",
    context=[shower_thought_task]
)

# Create Crew
thought_crew = Crew(
    agents=[content_writer],
    tasks=[shower_thought_task],
    verbose=True
)

thought_crew.kickoff()

file_path = "draft_thought.md"

instagram_long_access = os.getenv("INSTAGRAM_ACCESS_TOKEN")

if not os.path.exists(file_path):
    print(f"File '{file_path}' does not exist.")
    raise FileNotFoundError("The given markdown file does not exist brother... what you doin!? I know errors are DUMB but its ok you can do it 👍")

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Strip trailing and leading whitespaces from all lines
cleaned_lines = [line.strip() for line in lines if line.strip() != ""]

if not cleaned_lines:
    print("The file is empty or contains only whitespace.")
    raise ValueError("The file is EMPTYYYY BROTHAAAAR!!!!")

# First non-empty line is the title
first_line = cleaned_lines[0]
run_discord_bot(first_line)


file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gif.gif')

# Check if the file exists
if os.path.exists(file_path):
    print("The file 'gif.gif' exists in the same folder.")
else:
    gif_crew = Crew(
        agents=[gif_finder],
        tasks=[gif_task]
    )
    gif_crew.kickoff()