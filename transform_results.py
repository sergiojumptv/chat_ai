import chat_vertex
from chat_vertex import InputOutputTextPair,petition
import logging
logging.basicConfig(level=logging.INFO, filename='app.log')

logger = logging.getLogger(__name__)
system="Given a question and a table, the question must be answered with the data from the table and when finishes. Instead of carriage returns use <br>. Sometimes same question will have differents table so is important to adapt to the table "
examples=[]
InputOutputTextPair(input_text= f"""Question= Give me a ranking according to the total content duration for each title today.
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
}}]""",output_text=f"""The ranking according to the total content duration for each title today, along with their durations in minutes, is as follows: <br>1. "Nature of Love" - Total Duration: 1705212000 minutes <br>2. "A Royal Runaway Romance" - Total Duration: 1506960000 minutes <br>3. "The Sweetest Heart" - Total Duration: 944448000 minutes""")
def transform(msg):
    message=f"""Question= {msg.get('question')}
Table= {msg.get('result')}"""
    logging.info(message)
    return petition(system,[],examples,message)