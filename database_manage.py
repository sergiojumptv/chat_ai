import mysql.connector
import json
import uuid
with open('conversations_vertex.json','r') as f:
    data=json.load(f)







connection = mysql.connector.connect(host="34.85.133.207",
    user="sergio_remote",
    password="peterpan",
    database="conversations_chat")
    


# Establecer la conexión

# Crear un cursor
cursor = connection.cursor()

# Confirmar los cambios en la base de datos

# Agregar un usuario


def agregarUsuario(user_name):
    try:
        # Añadir un usuario
        sql_insert_user = "INSERT INTO user_ (user_name) VALUES (%s)"
        cursor.execute(sql_insert_user, (user_name,))
        connection.commit()
        print("Usuario agregado exitosamente.")
        return True
    except mysql.connector.IntegrityError as e:
        # Capturar la excepción si el usuario ya existe
        print(f"Error: El usuario '{user_name}' ya existe.")
        connection.rollback()
        return False 
def agregarConversacion(conversation_name,user_name):
    try:
        # Añadir una conversación relacionada con el usuario
        sql_insert_conversation = "INSERT INTO conversation ( conversation_name, user_name) VALUES (%s, %s)"
        cursor.execute(sql_insert_conversation, ( conversation_name, user_name))
        connection.commit()
        print("Conversación agregada exitosamente.")
    except mysql.connector.IntegrityError as e:
        # Capturar la excepción si la conversación ya existe
        print(f"Error: La conversación '{conversation_name}' ya existe.")
        connection.rollback()
def agregarMensaje(message_uuid, prev_uuid, message_text, author, feedback, user_name,conversation_name,msg_type='sql',origin=None):
    try:
        # Añadir los dos mensajes relacionados con la conversación
        sql_insert_message = "INSERT INTO message (uuid, prev_uuid, content, author, feedback, conversation_name, user_name, msg_type, origin) VALUES (%s,%s, %s, %s, %s,%s, %s, %s, %s)"
        cursor.execute(sql_insert_message, (message_uuid,prev_uuid, message_text,author, feedback, conversation_name,user_name,msg_type,origin))
        connection.commit()
        print("Mensajes agregados exitosamente.")
    except mysql.connector.IntegrityError as e:
        # Capturar la excepción si alguno de los mensajes ya existe
        print(f"Error: Un mensaje ya existen en la conversación.", e)
        connection.rollback()
    
def buscarUsuario(nombre_usuario):
    sql = "SELECT COUNT(*) FROM user_ WHERE user_name = %s"
    cursor.execute(sql, (nombre_usuario,))

    # Obtener el resultado de la consulta
    count = cursor.fetchone()[0]
    return count > 0
def buscarPrompt(nombre_usuario,conversation_name):
    sql = "SELECT COUNT(*) FROM conversation WHERE user_name = %s and conversation_name = %s "
    cursor.execute(sql, (nombre_usuario,conversation_name))

    # Obtener el resultado de la consulta
    count = cursor.fetchone()[0]
    return count > 0

def getAllConversationsNames(user_name):
    sql = "SELECT * FROM conversation WHERE user_name = %s"
    cursor.execute(sql, (user_name,))

    # Obtener todas las filas de la consulta
    nombres_conversaciones = [row[0] for row in cursor]
    return nombres_conversaciones

def getAllConversationsPrompts(user_name):
    conversaciones={}
    for prompt in getAllConversationsNames(user_name):
        conversaciones[prompt]=getConversation(user_name,prompt)
    return conversaciones
def getAllConversationsPromptsTexts(user_name):
    conversaciones={}
    for prompt in getAllConversationsNames(user_name):
        conversaciones[prompt]=getConversation(user_name,prompt,msg_type='text')
    return conversaciones

def getConversation(user_name,conversation_name,msg_type='sql'):
    try:
        sql = "SELECT * FROM message WHERE user_name = %s and conversation_name = %s and msg_type = %s "
        cursor.execute(sql, (user_name,conversation_name,msg_type))
        unordered_messages=[]
        messages=[]
        for uuid_, prev_uuid,content, author, feedback, otra,otra2,msg_type in cursor:
            if author=='bot':
                message={
                    'uuid':uuid_,
                    'prev_uuid':prev_uuid,
                    'content':content,
                    'author':author,
                    'feedback':feedback,
                    "citationMetadata": {
                        "citations": []
                    }
                }
                unordered_messages.append(message)
            elif author=='user':
                message={
                    'uuid':uuid_,
                    'prev_uuid':prev_uuid,
                    'content':content,
                    'author':author,
                    'feedback':feedback
                }
                unordered_messages.append(message)
            elif author=='system':
                message={
                    'author':author,
                    'content':content,
                    'feedback':"",
                    'uuid':str(uuid.uuid4()),
                    'prev_uuid':"",
                }
                messages.append(message)
            
        
        bloque_genesis=None
        for message in unordered_messages:
            
            if not message['prev_uuid'] and message['author'] != 'system':
                bloque_genesis=message
                break
        if bloque_genesis is None:
            return None
        messages.append(bloque_genesis)

        hash_anterior=messages[1]['uuid']
        while True:

            bloque_siguiente=None
            for message in reversed(unordered_messages):
                if message['prev_uuid']==hash_anterior :
                    bloque_siguiente=message
                    hash_anterior=message['uuid']
                    break
            if bloque_siguiente == None:
                break
            else:
                messages.append(bloque_siguiente)
        return messages
    except mysql.connector.IntegrityError as e:
        # Capturar la excepción si alguno de los mensajes ya existe
        print(f"Error: Un mensaje ya existen en la conversación.", e)
        connection.rollback()
        return None

def createPromptConversation(username,prompt):
    conversation = getConversation('default_user','default_prompt')
    agregarConversacion(prompt,username)
    hash_anterior=""
    system=conversation[0]
    agregarMensaje(system['uuid'],system['prev_uuid'],system['content'],system['author'],"",username,prompt)
    for msg in conversation[1:]:
        uuid_gen=str(uuid.uuid4())
        msg['uuid']=uuid_gen
        msg['prev_uuid']=hash_anterior
        agregarMensaje(uuid_gen,hash_anterior,msg['content'],msg['author'],msg["feedback"],username,prompt)
        hash_anterior=uuid_gen
    return conversation

def getDefaultLength():
    conversation = getConversation('default_user','default_prompt')
    tam=len(conversation)
    return tam

def give_feedback(prompt,uuid,feedback):
    try:
        # Crear el cursor
        cursor = connection.cursor()

        # Construir la consulta SQL para actualizar el usuario
        sql_update_user = "UPDATE message SET feedback=%s WHERE uuid=%s and conversation_name=%s"
        valores = tuple((feedback,uuid,prompt))

        # Ejecutar la consulta
        cursor.execute(sql_update_user, valores)
        connection.commit()
        return True
    except mysql.connector.Error as e:
        # Capturar la excepción en caso de error
        print(f"Error al actualizar el usuario': {str(e)}")
        connection.rollback()
        return False

def clearChats(username):
    try:

        if username != 'default_user':
            conversations=getAllConversationsNames(username)
            sql_delete = "DELETE FROM conversation WHERE user_name = %s and conversation_name = %s"
            
            for conver in conversations:
                
                cursor.execute(sql_delete, (username,conver))

            connection.commit()

            print(f"Registro eliminado exitosamente.")
            return True
        else:
            return False
    except mysql.connector.Error as e:
        # Capturar la excepción en caso de error
        print(f"Error al eliminar el registro: {str(e)}")
        connection.rollback()
        return False
    
if __name__ == '__main__':
    pass