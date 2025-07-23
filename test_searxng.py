from factool.knowledge_qa.searxng_wrapper import SearxNGAPIWrapper

searx = SearxNGAPIWrapper()
results = searx.search("What is the capital of Germany?")

for res in results:
    print(f"- {res.get('title')}: {res.get('url')}")
