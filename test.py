import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"query": "Where does the chest have the best leverage?"}
)
print(response.json()["answer"])