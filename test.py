import json
import database_manage as db
import uuid
user="default_user"
prompt="default_prompt"

# db.agregarUsuario(user)
# db.agregarConversacion(prompt,user)

with(open("conversations_vertex copy 2.json","r") as f):
    conver_o=json.load(f)
conver=conver_o[user][prompt]
l_uuid=""



x=conver[0]
print(x["uuid"],"  -  ",x["prev_uuid"])
#db.agregarMensaje(x["uuid"],x["prev_uuid"],x["content"],"system","",user,prompt)

for x in conver[1:]:
    n_uuid=str(uuid.uuid4())
    db.agregarMensaje(n_uuid,l_uuid,x["content"],x["author"],"",user,prompt)
    l_uuid=n_uuid