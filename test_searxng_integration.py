import os
import asyncio

# Set environment before importing factool
os.environ['FACTOOL_USE_SEARXNG'] = 'true'
os.environ['SEARXNG_URL'] = 'http://localhost:8080'

from factool import Factool

async def test_searxng():
    factool_instance = Factool("gpt-3.5-turbo")
    
    inputs = [
        {
            "prompt": "Who founded Microsoft?",
            "response": "Microsoft was founded by Bill Gates and Paul Allen in 1975.",
            "category": "kbqa"
        }
    ]
    
    results = factool_instance.run(inputs)
    print("Results:", results)

if __name__ == "__main__":
    asyncio.run(test_searxng())