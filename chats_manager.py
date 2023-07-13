import json
with open('conversations_vertex.json','r') as f:
    data=json.load(f)
for key,value in data.items():
    for key2,value2 in value.items():
        for dic in value2:
            if dic['author'] == 'bot':
                dic["feedback"]=""

with open('conversations_vertex.json', 'w') as f:
    json.dump(data,f)
