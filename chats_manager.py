import database_manage as db
data=db.getConversation("sergio","pepejuan")
for msg in data:
    print(msg['content'])