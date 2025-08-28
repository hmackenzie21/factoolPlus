from factool import Factool
factool_instance = Factool("gpt-4")

inputs = [
    {
        "prompt": "What is the capital city of France?",
        "response": "The capital city of France is Paris.",
        "category": "kbqa"
    },
]

response_list = factool_instance.run(inputs)
print(response_list)