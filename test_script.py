from factool import Factool
factool_instance = Factool("gpt-3.5-turbo")

inputs = [
    {
        "prompt": "Who is Dr Brian Cox",
        "response": "Dr Brian Cox is a physicist and Professor at University of Manchester",
        "category": "kbqa"      
    },
]

response_list = factool_instance.run(inputs)
print(response_list)