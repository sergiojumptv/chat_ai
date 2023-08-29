from chat_vertex import InputOutputTextPair, petition
import logging
import results_manage
logging.basicConfig(level=logging.INFO, filename='app.log')

logger = logging.getLogger(__name__)
system = "Given a question and a table, the question must be answered with the data from the table and when finishes. Instead of carriage returns use <br>. Sometimes same question will have differents table so is important to adapt to the table "
examples = []
InputOutputTextPair(input_text=f"""Question= Give me a ranking according to the total content duration for each title today.
Table= [{{
  "title": "Nature of Love",
  "duracion_minutos": "1705212000",
  "ranking": "1"
}}, {{
  "title": "A Royal Runaway Romance",
  "duracion_minutos": "1506960000",
  "ranking": "2"
}}, {{
  "title": "The Sweetest Heart",
  "duracion_minutos": "944448000",
  "ranking": "3"
}}]""", output_text=f"""The ranking according to the total content duration for each title today, along with their durations in minutes, is as follows: <br>1. "Nature of Love" - Total Duration: 1705212000 minutes <br>2. "A Royal Runaway Romance" - Total Duration: 1506960000 minutes <br>3. "The Sweetest Heart" - Total Duration: 944448000 minutes""")


def transform(table, question, prompt):
    message = f"""Question= {question}
Table= {table}"""
    prompt = create_prompt(prompt)

    return petition(system, prompt, examples, message)


def create_prompt(prompt: list):
    print("transforming")
    messages = []
    results = results_manage.getAllDocuments()
    for message in prompt:
        if message["author"] == 'user':
            input_text = message["content"]

        elif message["author"] == 'bot':
            target_uuid = message["uuid"] if "uuid" in message else print(
                "no uuid")
            for diccionario in results:
                if "_id" in diccionario and isinstance(diccionario["_id"], str) and target_uuid in diccionario["_id"]:
                    print("id encontrado:", diccionario["_id"])
                    results_add = diccionario["results"]
                else:
                    print("*")
            output_text=message["content"]

            #output_text = "Question= "+message["content"]+"Table= "+str(results_add)
            
            completed_input_text="Question= "+input_text+" Table= "+str(results_add)
            inout = (completed_input_text, output_text)
            print("output=",inout, end="****************\n")
            messages.append(inout)

    return messages
