from google.cloud import bigquery
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
from chat_vertex import vertex_petition
from flask_session import Session
import asyncio
import os
import uuid
import database_manage as db
import logging
import logging.config
import transform_results
import results_manage
import yaml

with open('logging_config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)



app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
# Almacenamiento de sesión en el sistema de archivos
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
CORS(app)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'bigquery_credentials.json'
client = bigquery.Client()
vertex_credentials = '/root/.config/gcloud/application_default_credentials.json'
bigquery_credentials = 'bigquery_credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = bigquery_credentials
with open("config.json", "r") as f:
    config_data=json.load(f)

class Chat():
    
    #obtener todas las conversaciones de un usuario
    def get_conversations(self):
        self.conversations=db.getAllConversationsPrompts(self.username)
        self.conversations_text=db.getAllConversationsPromptsTexts(self.username)
        return self.conversations
    
    #inicializacion de objeto chat
    def __init__(self, username):
        self.username = username
        if not db.buscarUsuario(self.username):
            db.agregarUsuario(self.username)
        self.get_conversations()
        self.tam_default_len = db.getDefaultLength()
        self.respon = ""
        self.result = []
        self.current_prompt = ""
        self.conversations_prepared = {}
    
    #borrar conversaciones
    def clearChats(self):
        db.clearChats(self.username)
        self.conversations={}
    
    #dar feedback sobre una query
    def give_feedback(self, feedback: dict):
        for message in self.conversations[feedback["prompt"]]:
            if message['author'] == 'bot':
                if 'uuid' in message:
                    if message["uuid"] == feedback['uuid']:
                        message["feedback"] = feedback['feedback']
                        db.give_feedback(feedback.get('prompt'),feedback.get('uuid'),feedback.get('feedback'))
                        
        
    
    
    #guardar mensaje en conversacion o guardar conversacion
    def include_in_conversation(self, include=None,result_text=None,uuid_user=None,results=None, prompt='default_prompt', role='user',feedback=""):
        prev_uuid=""
        for message in self.conversations.get(prompt):
            prev_uuid=message.get("uuid")
        gen_uuid = str(uuid.uuid4())
        prev_uuid_text=""
        if (conversations_text := self.conversations_text.get(prompt)) is not None:
            for message in conversations_text:
                prev_uuid_text = message.get("uuid")
        gen_uuid_text = str(uuid.uuid4())
        prepared = {"author": "user", "content": f"{include}", "uuid": gen_uuid,"prev_uuid":prev_uuid} if role == 'user' else {
            "content": f"{include}",
            "author": "bot",
            "citationMetadata": {"citations": []},
            "feedback": "",
            "uuid": gen_uuid,
            "prev_uuid":prev_uuid}
        prepared_text = {"author": "user", "content": f"{result_text if result_text else include}", "uuid": uuid_user,"prev_uuid":prev_uuid_text} if role == 'user' else {
            "content": f"{result_text if result_text else include}",
            "author": "bot",
            "citationMetadata": {"citations": []},
            "feedback": "",
            "uuid": gen_uuid_text,
            "prev_uuid":prev_uuid_text}
        

        

        if prompt != 'default_prompt':
            self.conversations[prompt].append(prepared)
            self.conversations_text[prompt].append(prepared_text)
            logging.warning(f"{gen_uuid},{prev_uuid},{include},{role},{feedback},{self.username},{prompt}")
            logging.warning(f"{uuid_user if role=="user" else gen_uuid_text},{prev_uuid_text},{result_text if result_text else include},{role},{feedback},{self.username},{prompt},msg_type={'text'},origin={gen_uuid}")
            db.agregarMensaje(gen_uuid,prev_uuid,include,role,feedback,self.username,prompt)
            db.agregarMensaje(uuid_user if role=="user" else gen_uuid_text,prev_uuid_text,result_text if result_text else include,role,feedback,self.username,prompt,
                              msg_type='text',origin=gen_uuid)
            if result_text and results:
                results_manage.agregarResultados(gen_uuid_text,results)
        return gen_uuid_text

    #reducir tokens de conversacion
    def reduce_tokens(self):

        del self.conversations[self.current_prompt][
            self.tam_default_len]
    #encontrar query
    def find_start(self, string_principal):

        indice1 = string_principal.lower().find('select')
        indice2 = string_principal.lower().find('with')

        if indice1 == -1 and indice2 == -1:
            return -1  # Si ninguno de los dos strings es encontrado

        if indice1 == -1:
            return indice2  # Si solo se encuentra el segundo string

        if indice2 == -1:
            return indice1  # Si solo se encuentra el primer string

        return min(indice1, indice2)
    
    #comprobar si hay una query en la respuesta de la ia y si es asi devolverla
    def select_sintax(self, respon):
        if respon.lower().find('i am trained to understand and respond') != -1:
            return respon, True
        select_index = self.find_start(respon)
        if select_index == -1:
            return respon, True
        select = respon[select_index:]
        for x in select:
            if x == '\n':
                select = select.replace('\n', " ")

        for i in range(len(select) - 1, -1, -1):
            if select[i] == "" or select[i] == " " or select[i] == '`':
                select = select[:i] + select[i + 1:]
            else:
                break
            
        select.replace("'''", "")
        select.replace("```", "")

        return select, False
    
    #ejecucion de query
    def execute(self, query):
        # print('execting...')
        query_job = client.query(query)
        # print("\033[2J\033[H", 'executing...')
        rows = []
        for row in query_job.result():
            row_dict = {}
            for field_name, value in row.items():
                row_dict[field_name] = str(value)
            rows.append(row_dict)
        self.result = rows
        return rows
    
    #generaciond e query
    def gpt_select(self, prompt):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = vertex_credentials
        response = asyncio.run(vertex_petition(prompt))
        # if response['usage']['total_tokens']>3300:
        # self.reduce_tokens()
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = bigquery_credentials
        # print(response)

        return response
    
    #intentar resolver error
    def try_error(self, prompt, select, e):
        valid = False
        total = 3
        for _ in range(total):
            total -= 1

            prepared_assistant = {
                "content": f"{select}",
                "author": "bot",
                "citationMetadata": {
                    "citations": []
                }
            }
            # print("***************************************")
            prepared_user = {
                "author": 'user',
                "content": f"La query a dado el siguiente error: {e}. \n intenta hacer la query solucionando el error"
            }
            error_conver = prompt.copy()
            if 'try_error' not in self.conversations:
                self.conversations['try_error'] = error_conver

            self.conversations['try_error'].append(prepared_assistant)
            self.conversations['try_error'].append(prepared_user)

            response = self.gpt_select(self.conversations['try_error'])

            select, no_select = self.select_sintax(response)
            try:
                if no_select:

                    # print(response)
                    return response
                else:
                    self.execute(select)
                    valid = True

            except Exception as error:
                e = error
                # print('Error: ',e,'\nReintentando...')

            if valid:
                break

        return response, no_select
    
    #ejecutar la peticion del mensaje: obtener query y ejecutarla en caso de ser ejecutable
    def make_petition(self, prompt):
        repeat = 0
        while True:
            response = self.gpt_select(prompt)

#            self.tokens_used = response['usage']['total_tokens']
            # print('tokens usados', self.tokens_used)
            # print('coste de uso', self.tokens_used/1000*0.002, '$')
            try:
                self.respon = response

                select, no_select = self.select_sintax(response)
                if no_select:
                    logging.info(response)
                    return response, no_select

                self.execute(select)
                self.conversations_prepared = self.conversations.copy(
                )[self.current_prompt][-1]['result'] = self.result.copy()
                # for key in result:
                # print(str(key))
                # print(select)

                break
            except Exception as e:
                if repeat < 1:
                    # print('error: ', e)
                    repeat += 1
                    preview_prompt = self.current_prompt
                    self.current_prompt = 'try_error'
                    select, no_select = self.try_error(prompt, select, e)
                    self.current_prompt = preview_prompt
                    logging.info(self.result)
                    self.conversations.pop('try_error')
                    return select, no_select
                else:
                    # print("imposible hacer la select")
                    break

        '''
        with open('querys_gpt.json', 'w') as f:
            json.dump(result, f)
        '''
        logging.info(f"response= {response}, result {self.result}")

        return response, no_select
    
    #comprobar si cumple ciertos requisitos el mensaje
    def valid(self, user_input):
        commands = ['/new_chat', '/exit', '/save', '/use']
        if user_input != '':

            for command in commands:
                if user_input.split()[0] in command and user_input[0] == '/':
                    if user_input == '/new_chat':
                        return False
                    elif user_input == '/exit':
                        return False
                    elif "/save" in user_input and len(user_input.split()) > 1:
                        return False
                    elif '/use' in user_input and len(user_input.split()) > 1:
                        return False
                    else:
                        print()
                        # print(f'Comando {user_input} no valido\n Comandos validos:\n\t /new_chat,\n\t /exit,\n\t /save <nombre a guardar>,\n\t /use <nombre a guardar>')
            return True
        else:
            return False
    
    #funcion para chatear
    def newChat(self, msg, gen_uuid, prompt='default_prompt'):
        transformed_result=None
        self.include_in_conversation(
            include=msg,uuid_user=gen_uuid, prompt=prompt)
        query, no_select = self.make_petition(
            self.conversations[prompt])
        if not no_select:
            transformed_result=transform_results.transform(self.result,msg,self.conversations_text.get(prompt))
            respon_uuid=self.include_in_conversation(
            query,result_text=transformed_result,results=self.result, prompt=prompt, role='bot')
        else:
            respon_uuid=self.include_in_conversation(
            query, prompt=prompt, role='bot')

        '''for res in self.result:
            print(res)'''

        # print('Respuesta: ', self.respon)
        # print('tokens usados', self.tokens_used)
        # print('coste de uso', self.tokens_used/1000*0.002, '$')
        # print('prompt: ', self.current_prompt)
        respon=transformed_result if transformed_result else query
        return respon, no_select, respon_uuid
    
    #llamar a funcion para chatear
    def chat(self, gen_uuid="", msg='/new_chat'):
        # try:
        self.result.clear()
        chat, no_select, respon_uuid = self.newChat(
            msg, gen_uuid, prompt=self.current_prompt)
        '''except Exception as e:
            print(e)
            self.conversations['default_prompt']=self.original_prompt
            self.include_in_conversation(conversations)'''
        return chat, no_select, respon_uuid
    
    #crear conversacion y agregarle el default_prompt
    def createConversation(self, prompt):
        db.createPromptConversation(self.username, prompt)
        self.get_conversations()
        

    
    #obtener nombres de las conversaciones
    def getConversationsName(self):
        return list(self.conversations.keys())


'''def main(cant):

    lock = threading.Lock()
    barrier = threading.Barrier(cant)

    tareas = []
    for _ in range(cant):
        chat = Chat(lock, barrier)
        tareas.append(chat)

    for tarea in tareas:
        tarea.start()
    for tarea in tareas:
        tarea.join()'''
# tarea.start()
# for tarea in tareas:
# tarea.join()

# SELECT * FROM `hallmark-hallmark-pro.hallmark_hallmark_dwh.fact_registereduser` WHERE daydate  =DATE "2022-05-11" and userid='bc6f6da1-0b90-48ab-85f8-b01bb4097901'
# type tiene dods valores posibles subscription y registration  de la tabla fact_registereduser
# status puede tener PayingSubscription TrialSubscription para los subscription
# register y playback
# para registered user la columna subscriptionperiod muestra el tipo de subscripcion y activationdaydate para cuando se dio de alta
chats = {}

# generar un id


@app.route("/generate_uuid", methods=['GET'])
def generate_uuid():
    uuid_generated = str(uuid.uuid4())

    return jsonify({"uuid": uuid_generated})

# obtener mensajes de una conversacion


@app.route("/get_conversation_of_prompt", methods=['POST'])
def get_conversation_of_prompt():
    
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session.get('username')
    if username not in chats:
        chats[username] = Chat(username)
    chat: Chat = chats[username]
    prompt = request.get_json()["name"]
    
    if prompt not in chat.conversations:
        
        chat.createConversation(prompt)
    conversation = chat.conversations_text.get(prompt)
    chat.current_prompt = prompt
    messages = []
    
    for item in conversation:
        msg = {
            "author": item["author"],
            "content": item["content"],
            "uuid": item["uuid"]
        }

        if item["author"] == "bot":
            msg["feedback"] = item["feedback"]

        messages.append(msg)
    
    return jsonify(messages)

# crear conversacion de un usuario


@app.route("/save-prompt", methods=['POST'])
def save_prompt():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session.get('username')
    chat: Chat = chats[username]
    prompt = request.get_json()["name"]
    chat.createConversation(prompt)
    return jsonify({'reply': "saved"})

# obtener todas los nombres de las conversaciones de un usuario


@app.route('/get_prompts', methods=['GET'])
def get_prompts():

    if 'username' not in session:
        # print(session.get('username'))
        return redirect(url_for('login'))
    username = session.get('username')
    if username not in chats:
        chats[username] = Chat(username)
    chat: Chat = chats[username]
    prompts = chat.getConversationsName()
    return jsonify(prompts)

# dar feedback sobre una query


@app.route('/give_feedback', methods=['POST'])
def give_feedback():
    data = request.json
    # Acceder a los datos enviados en la solicitud POST

    if 'username' not in session:
        # print(session.get('username'))
        return redirect(url_for('login'))
    username = session.get('username')
    if username not in chats:
        chats[username] = Chat(username)
    chat = chats[username]
    feedback_complete = {
        "prompt": data['prompt'],
        "uuid": data['uuid'],
        "feedback": data["feedback"]
    }
    

    chat.give_feedback(feedback_complete)
    return 'Solicitud POST exitosa'


@app.route('/clear_chats', methods=['GET'])
def clear_chats():
    if 'username' not in session:
        
        return redirect(url_for('index'))
    username=session.get('username')
    chat=chats[username]
    chat.clearChats()
    return '', 200

# enviar un mensaje


@app.route('/send_message', methods=['POST'])
def sendmessage():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session.get('username')
    chat = chats[username]
    requestt = request.get_json()
    ex_request = requestt['text']
    gen_uuid = requestt['uuid']
    logging.info("user: "+ username+" sending message on prompt: "+chat.current_prompt)
    petition, no_select, gen_uuid = chat.chat(gen_uuid, ex_request)
    if not no_select:
        return jsonify({'reply': petition, 'result': chat.result, 'uuid': gen_uuid})
    return jsonify({'reply': petition, 'uuid': gen_uuid})

# iniciar sesion de usuario o crearlo en caso de no existir


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        request_json = request.get_json()
        username = request_json.get('username')
        if 'username' not in session and username:
            chats[username] = Chat(username)
        logging.info("logged user: "+ username)
        session['username'] = username
        return redirect(url_for('chat_web'))
    else:
        return render_template('auth/login.html', config_data=config_data)

# cargar html del chat


@app.route('/chat')
def chat_web():
    if 'username' in session:
        return render_template('web.html', config_data=config_data)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat_web'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
