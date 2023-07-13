import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
import os
vertex_credentials = '/root/.config/gcloud/application_default_credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = vertex_credentials
vertexai.init(project="services-pro-368012", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison@001")


def petition(prompt,context,message):
    parameters = {
            "temperature": 0.7,  # Temperature controls the degree of randomness in token selection.
            "max_output_tokens": 1000,  # Token limit determines the maximum amount of text output.
            "top_p": 0.9,  # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
            "top_k": 40,  # A top_k of 1 means the selected token is the most probable among all tokens.
        }

    chat = chat_model.start_chat(
            context=context,
            examples=prompt
        )
    response = chat.send_message(message, **parameters)
    return response.text


    '''
    async def make_request(session,msg):
        global headers
        data["instances"][0]["messages"]=msg

        try:
            print(headers['Authorization'])
            async with session.post(url, headers=headers, data=json.dumps(data)) as response:

                if response.status != 200:
                        raise Exception("Error en la solicitud:", response.status)
                return await response.json()
        except Exception as e:
            print(e)
            resultado = subprocess.run(['gcloud', 'auth', 'print-access-token'], capture_output=True, text=True)
            if resultado.returncode == 0:
                token_acceso = resultado.stdout.strip()
                print("Token de acceso:", token_acceso)
            else:
                error = resultado.stderr.strip()
                print("Error al obtener el token de acceso:", error)
            headers = {
                "Authorization": f"Bearer {token_acceso}" ,
                "Content-Type": "application/json"
            }   
            async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                return await response.json()



    async def vertex_petition(msg):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(1):
                tasks.append(asyncio.create_task(make_request(session,msg)))

            responses = await asyncio.gather(*tasks)

            for response in responses:
                if 'error' in response:
                    return str(response)
                return response.get("predictions")[0]["candidates"][0]["content"]

    '''
async def vertex_petition(prompt:list):
    new_prompt=[]
    for message in prompt:
        if message["author"]=='user':
            input_text=message["content"]
        elif message["author"]=='bot':
            output_text=message["content"]
            inout=InputOutputTextPair(input_text=input_text,output_text=output_text)
            new_prompt.append(inout)
    context=prompt[0]['content']
    message=prompt[-1]['content']
    return petition(new_prompt,context,message)
    