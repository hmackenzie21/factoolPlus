from factool import Factool
factool_instance = Factool("gpt-4")

inputs = [
    {
        "prompt": "What is Donald Trump's most recent statement on Ukraine?",
        "response": "President Donald Trump vowed to ‘get it done’ and end the war in Ukraine on Truth Social",
        "category": "kbqa"
    },
]

response_list = factool_instance.run(inputs)
print(response_list)