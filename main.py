import warnings
import os
import json
from crewai_tools import CSVSearchTool
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew
from crewai import LLM
from pydantic import BaseModel, Field
from typing import Type
from discordbot import run_discord_bot
import threading
import time
import requests


# Get a showerthought

with open("showerthoughts.json", "r") as f:
    data = json.load(f)
    thought = data.pop()
    
# Update showerthoughts.json file

with open('showerthoughts.json', 'w') as f:
    json.dump(data, f, indent=4)

warnings.filterwarnings('ignore')

os.environ['GOOGLE_API_KEY'] = "AIzaSyAsOcKmk-zh9sPZM5gWprOnmsG4xnIr4x0"

llm = LLM(
    provider="google",
    model="gemini/gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    api_key="AIzaSyAsOcKmk-zh9sPZM5gWprOnmsG4xnIr4x0"
)

# Custom tool to search gif
class MyToolInput(BaseModel):
    query: str = Field(..., description="Keywords to find a related GIF")

class GIFSearchTool(BaseTool):
    name: str = "GIF Search tool"  # Added type annotation
    description: str = "Search a gif based on provided keywords"  # Added type annotation
    args_schema: Type[BaseModel] = MyToolInput  # Proper annotation

    def _run(self, query: str) -> str:
        api_key = "vZ7hCK3M3NfHwoTPX9ypgZPucKOhhxVE"
        response = requests.get(
            "https://api.giphy.com/v1/gifs/search",
            params={'api_key': api_key, 'q': query, 'limit': 1}
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

gif_finder = Agent(
    role="GIF Curator",
    goal="Find the perfect GIF for the selected shower thought",
    backstory="A visual specialist with a knack for matching abstract thoughts to GIFs."
            "You know are well aware of those keywords that can be used to search GIFs"
            "that contains a touch of a confused and deep thinking type look while being"
            "related to the theme of the thought.",
    tools=[giphy_tool],
    verbose=True,
    llm=llm
)

tags_finder = Agent(
    role="Instagram Tag SEO specialist",
    goal="Find the perfect tags for the selected shower thought",
    backstory="A specialist in finding perfect and most popular tags for" \
    "intsgram reels that ressemble the shower thought.",
    verbose=True,
    llm=llm
)


# Define Tasks

gif_task = Task(
    description=(
        "Find a suitable GIF for the shower thought '{thought}'"
        "using the GIFSearchTool to find and save the GIF by using keywords"
        "that closely ressembles the theme of the thought while maintaining"
        "the thinking and confused type look."
    ),
    agent=gif_finder,
    expected_output="Confirmation that the GIF was saved as gif.gif",
)


class Tags(BaseModel):
    tags:list

tags_task = Task(
    description=(
        "Find suitable tags for the shower thought '{thought}'"
    ),
    agent=tags_finder,
    output_json=Tags,
    output_file="showerthought.json",
)

# Create and run the crew
thought_crew = Crew(
    agents=[gif_finder, tags_finder],
    tasks=[gif_task, tags_task],
    verbose=True
)

thought_crew.kickoff(inputs={"thought":thought})

with open("showerthought.json", "r") as f:
    data = json.load()
with open("showerthought.json", "r") as f:
    data["thought"] = thought
    json.dump(data, f, indent=4)
    

run_discord_bot(thought)