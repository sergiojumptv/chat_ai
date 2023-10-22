import vertexai
from custom_vertex import ChatModel, InputOutputTextPair
import os
#vertex_credentials = '/root/.config/gcloud/application_default_credentials.json'
vertex_credentials = 'application_default_credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = vertex_credentials
vertexai.init(project="services-pro-368012", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison@001")




def petition(context,messages,examples,message):
    chat_model = ChatModel.from_pretrained("chat-bison@001")

    chat = chat_model.start_chat(
        history=messages,context=context,examples=examples
        )

    response = chat.send_message(message,max_output_tokens=1000)


    return response.text



   
async def vertex_petition(prompt:list):
    examples=[]
    messages=[]
    for message in prompt[23:]:
        if message["author"]=='user':
            input_text=message["content"]
        elif message["author"]=='bot':
            output_text=message["content"]
            inout=(input_text,output_text)
            messages.append(inout)
    for message in prompt[:23]:
        if message["author"]=='user':

            input_text=message["content"]
        elif message["author"]=='bot':
            output_text=message["content"]
            inout=InputOutputTextPair(input_text= input_text,output_text=output_text)
            examples.append(inout)
    context=prompt[0]['content']
    message=prompt[-1]['content']

    return petition(context,messages,examples,message)
   
