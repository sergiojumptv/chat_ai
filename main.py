from google.cloud import bigquery
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
from chat_vertex import vertex_petition
from flask_session import Session

import os
import uuid
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SESSION_TYPE'] = 'filesystem'  # Almacenamiento de sesión en el sistema de archivos
Session(app)
CORS(app)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'bigquery_credentials.json'
client = bigquery.Client()
vertex_credentials = '/root/.config/gcloud/application_default_credentials.json'
bigquery_credentials = 'bigquery_credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = bigquery_credentials


class Chat():

    def get_conversations(self):
        with open('conversations_vertex.json', 'r')as f:
            self.conversations = json.load(f)
        return self.conversations

    def __init__(self,username):
        self.username=username

        self.get_conversations()
        if self.username not in self.conversations:
            self.conversations[username]=self.conversations['default_user'].copy()
            self.include_in_conversation(new_user=True)
        self.original_prompt = self.conversations[self.username]['default_prompt'].copy()
        self.tam_default_len = len(self.original_prompt)
        self.respon = ""
        self.result = []

        self.tokens_used = 0

        self.current_prompt = "default_prompt"
        self.conversations_prepared={}

    def clearChat(self):
        self.conversations = {key: value for key, value in self.conversations.items() if key == 'default_prompt'}
        self.conversations['default_prompt']=self.original_prompt.copy()

    def give_feedback(self,feedback:dict):
        for message in self.conversations[self.username][feedback["prompt"]]:
            if message['author']=='bot':
                if 'uuid' in message:
                    if message["uuid"]==feedback['uuid']:
                        print('encontrado')
        print('busqueda completa')


    def include_in_conversation(self,include=None,gen_uuid="", prompt='default_prompt', role='user', save=False, new_user=False):
        prepared = {"author": "user", "content": f"{include}","uuid":gen_uuid} if role == 'user' else {
            "content": f"{include}",
            "author": "bot",
            "citationMetadata": {"citations": []},
            "feedback": "",
            "uuid":gen_uuid}

        if new_user:
            with open('conversations_vertex.json', 'w') as f:
                    json.dump(self.conversations, f)
        else:
            if not save:
                if prompt not in self.conversations[self.username]:
                    self.conversations[self.username][prompt] = self.original_prompt.copy()
                self.conversations[self.username][prompt].append(prepared)
            
            if prompt != 'default_prompt' and save:
                with open('conversations_vertex.json', 'r')as f:
                    current_convers = json.load(f)
                if prompt not in self.conversations[self.username]:
                    current_convers[self.username][prompt] = self.conversations[self.username]['default_prompt'].copy()
                    self.conversations[self.username][prompt] = self.conversations[self.username]['default_prompt'].copy()

                else:
                    current_convers[self.username][prompt]=self.conversations[self.username][prompt].copy()
                    

                current_convers[self.username]['default_prompt'] = self.original_prompt.copy()
                self.conversations[self.username]['default_prompt'] = self.original_prompt.copy()
                
                
                with open('conversations_vertex.json', 'w') as f:
                    json.dump(current_convers, f)

    def reduce_tokens(self):

        del self.conversations[self.current_prompt][self.tam_default_len]
        del self.conversations[self.current_prompt][self.tam_default_len]

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
            # print(respon[i])
        select.replace("'''", "")
        select.replace("```", "")

        return select, False

    def execute(self, query):

        # print('execting...')
        query_job = client.query(query)
        print("\033[2J\033[H", 'executing...')
        rows = []
        columns = []
        for row in query_job.result(timeout=5):
            for x in row:
                columns.append(x)
            rows.append(columns.copy())
            columns.clear()
        self.result = rows
        return rows

    def gpt_select(self, prompt):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = vertex_credentials
        '''response = asyncio.run(vertex_petition(prompt))'''
        # if response['usage']['total_tokens']>3300:
        # self.reduce_tokens()
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = bigquery_credentials
        #print(response)
        time.sleep(5)
        return 'response'

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
            print("***************************************")
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

                    #print(response)
                    return response
                else:
                    self.execute(select)
                    valid = True

            except Exception as error:
                e = error
                # print('Error: ',e,'\nReintentando...')

            if valid:
                break

        return response,no_select

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

                    return response,no_select

                self.execute(select)
                self.conversations_prepared=self.conversations.copy()[self.current_prompt][-1]['result']=self.result.copy()
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
                    select,no_select = self.try_error(prompt, select, e)
                    self.current_prompt = preview_prompt

                    self.conversations.pop('try_error')
                    return select,no_select
                else:
                    #print("imposible hacer la select")
                    break

        '''
        with open('querys_gpt.json', 'w') as f:
            json.dump(result, f)
        '''

        return response,no_select

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
                        print(
                            f'Comando {user_input} no valido\n Comandos validos:\n\t /new_chat,\n\t /exit,\n\t /save <nombre a guardar>,\n\t /use <nombre a guardar>')
            return True
        else:
            return False

    def newChat(self, msg,gen_uuid, prompt='default_prompt'):
        self.current_prompt = prompt

        self.include_in_conversation(include=msg, gen_uuid=gen_uuid, prompt=prompt)
        query,no_select = self.make_petition(self.conversations[self.username][prompt])
        respon_uuid=str(uuid.uuid4())
        self.include_in_conversation(query,gen_uuid=respon_uuid, prompt=prompt, role='assistant')

        '''for res in self.result:
            print(res)'''
        
        #print('Respuesta: ', self.respon)
        # print('tokens usados', self.tokens_used)
        # print('coste de uso', self.tokens_used/1000*0.002, '$')
        #print('prompt: ', self.current_prompt)

        return query,no_select,respon_uuid

    def chat(self,gen_uuid="", msg='/new_chat',):
        # try:
        self.result.clear()
        if msg == '':
            chat = '/new_chat'
        elif msg == '/new_chat':
            chat="new chat"
            self.current_prompt='default_prompt'
            no_select=True
            respon_uuid=""
        elif '/save' in msg:
            prompt = msg.split()[1]
            self.include_in_conversation(prompt=prompt, save=True)
            self.current_prompt = prompt
            print('saved...')
            chat = 'saved'
            no_select=True
            respon_uuid=""
        elif '/load' in msg:
            prompt = msg.split()[1]
            self.current_prompt = prompt
            chat = 'loaded'
            no_select=True
            respon_uuid=None
        else:
            chat,no_select,respon_uuid = self.newChat(msg, gen_uuid,prompt=self.current_prompt)
        '''except Exception as e:
            print(e)
            self.conversations['default_prompt']=self.original_prompt
            self.include_in_conversation(conversations)'''
        return chat,no_select,respon_uuid


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

@app.route("/generate_uuid", methods=['GET'])
def generate_uuid():
    uuid_generated=str(uuid.uuid4())

    return jsonify({"uuid":uuid_generated})
@app.route("/get_conversation_of_prompt", methods=['POST'])
def get_conversation_of_prompt():
    

    if 'username' not in session:
        #print(session.get("username"))
        return redirect(url_for('login'))
    username=session.get('username')
    if username not in chats:
        chats[username]=Chat(username)
    chat=chats[username]
    prompt = request.get_json()["name"]
    conversation = chat.conversations.get(username).get(prompt)

    chat.chat("/load " + prompt)
    messages = []
    for item in conversation[chat.tam_default_len:]:
        msg = {
            "author": item["author"],
            "content": item["content"],
        }
        print(item)
        if item["author"] == "bot":
            msg["feedback"] = item["feedback"]
        messages.append(msg)
    print(messages)
    return jsonify(messages)

@app.route("/save-prompt", methods=['POST'])
def save_prompt():
    if 'username' not in session:
        return redirect(url_for('index'))
    username=session.get('username')
    chat=chats[username]
    prompt = request.get_json()["name"]
    chat.chat(msg="/save " + prompt)
    return jsonify({'reply': "saved"})

@app.route('/get_prompts', methods=['GET'])
def get_prompts():
    print(session.get('username'))
    if 'username' not in session:
        #print(session.get('username'))
        return redirect(url_for('login'))
    username=session.get('username')
    if username not in chats:
        chats[username]=Chat(username)
    chat=chats[username]
    prompts = list(chat.conversations[username].keys())
    print(prompts)
    return jsonify(prompts)
@app.route('/give_feedback', methods=['POST'])
def give_feedback():
    data = request.json
    # Acceder a los datos enviados en la solicitud POST
    
    if 'username' not in session:
        #print(session.get('username'))
        return redirect(url_for('login'))
    username=session.get('username')
    if username not in chats:
        chats[username]=Chat(username)
    chat=chats[username]
    feedback_complete={
    "prompt" : data['prompt'],
    "uuid" : data['uuid'],
    "feedback" :data["feedback"]
    }
    chat.give_feedback(feedback_complete)
    return 'Solicitud POST exitosa'

'''@app.route('/clear_chats', methods=['GET'])
def clear_chats():
    if 'username' not in session:
        print(session)
        return redirect(url_for('index'))
    username=session.get('username')
    chat=chats[username]
    chat.clearChat()
    return '', 200'''

@app.route('/send_message', methods=['POST'])
def sendmessage():
    if 'username' not in session:
        return redirect(url_for('index'))
    username=session.get('username')
    chat=chats[username]
    requestt = request.get_json()
    ex_request = requestt['text']
    gen_uuid = requestt['uuid']
    print(type(gen_uuid))
    petition, no_select,gen_uuid = chat.chat(ex_request,gen_uuid)
    if not no_select:
        return jsonify({'reply': petition, 'result': chat.result,'uuid':gen_uuid})
    return jsonify({'reply': petition,'uuid':gen_uuid})
@app.route('/loginpage', methods=['POST'])

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        request_json=request.get_json()
        username = request_json.get('username')
        if username:
            chats[username]= Chat(username)
        session['username'] = username
        print(session.get('username'))
        return redirect(url_for('chat_web'))
    else:
         return render_template('auth/login.html')
@app.route('/chat') 
def chat_web():
    if 'username' in session:
        return render_template('web.html')
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
