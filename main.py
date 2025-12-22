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
import random
import requests
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

# # Get a showerthought

# with open("showerthoughts.json", "r") as f:
#     data = json.load(f)
#     thought = data.pop()
    
# # Update showerthoughts.json file

# with open('showerthoughts.json', 'w') as f:
#     json.dump(data, f, indent=4)


#Login to our instagram account


# Pull function to pull content from r/showerthoughts subreddit

def pull():
    url = "https://www.reddit.com/r/showerthoughts/top.json?t=month&limit=50"


    client_id = os.getenv("REDDIT_ID")
    secret_key = os.getenv("REDDIT_SECRET_KEY")

    auth = requests.auth.HTTPBasicAuth(client_id, secret_key)

    data = {
        'grant_type': "password",
        'username': os.getenv("REDDIT_ID"),
        'password': os.getenv("REDDIT_SECRET_KEY")
    }

    header = {
        'User-Agent' : "justabotman"
    }

    output = requests.get(url, auth=auth, data=data, headers=header)

    if output.ok:
        data = output.json()
        with open('showerthoughts.json', 'w') as file:
            data = data['data']['children']
            json.dump(data, file)

    else:
        pprint(output.text)
        print(f"error [{output.status_code}]")

print('#################################################################################################')

# This function is to choose a random showerthought from the showerthoughts.json file and then save it without the random choosen showerthought

def generate_thought():
    """Pick a thought, remove it from the pool, auto-refill if needed, and return it."""
    try:
        with open('showerthoughts.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    if not data:  # empty file → repull
        pull()
        with open('showerthoughts.json', 'r') as f:
            data = json.load(f)

    # Pick one random entry
    chosen = random.choice(data)

    # Remove it from the pool
    data = [d for d in data if d != chosen]

    # Save updated pool
    with open('showerthoughts.json', 'w') as f:
        json.dump(data, f, indent=4)

    return chosen

truth = True

# Sometimes subreddits have this post "Forging A Return to Productive Conversation: An Open Letter To Reddit" so the while loop makes sure that such post is removed 

thought = generate_thought()

thought = thought['data']['title']

print(thought)

warnings.filterwarnings('ignore')

os.environ['GOOGLE_API_KEY'] = "AIzaSyAcBV6GhMiBQbo3bDNPy15p91ovSau_898"

llm = LLM(
    provider="google",
    model="gemini-2.5-flash",
    verbose=True,
    temperature=0.5,
    api_key="AIzaSyAcBV6GhMiBQbo3bDNPy15p91ovSau_898"
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
        expected_output="A JSON file",
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
    data = json.load(f)
with open("showerthought.json", "w") as f:
    data["thought"] = thought
    json.dump(data, f, indent=4)
    

run_discord_bot(thought)