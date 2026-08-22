import asyncio
import requests

async def fetchData():
    response = requests.get("https://stacked-layer-backend.onrender.com/api/prompts/published")
    data = response.json()
    print(data)
    return data

asyncio.run(fetchData())