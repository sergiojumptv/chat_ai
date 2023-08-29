from pymongo import MongoClient

# Conectarse a la base de datos local (asegúrate de tener MongoDB ejecutándose)
def agregarResultados(uuid_gen, results):
    client = MongoClient('localhost', 27017)
    results_dict = {
        "_id": uuid_gen,
        "results":results
    }
    
    print(uuid_gen)

    # Nombre de la base de datos que deseas crear (por ejemplo, "mi_base_de_datos")
    nombre_base_datos = "results_chat"

    # Nombre de la colección donde insertarás el documento (por ejemplo, "mi_coleccion")
    nombre_coleccion = "results"
    collection=client[nombre_base_datos][nombre_coleccion]
    # Datos para el documento que insertarás en la colección
    collection.insert_one(results_dict)
    print("results_added")

    # Cerrar la conexión
    client.close()

def getAllDocuments():
    client = MongoClient('localhost', 27017)

    # Nombre de la base de datos que deseas crear (por ejemplo, "mi_base_de_datos")
    nombre_base_datos = "results_chat"

    # Nombre de la colección donde insertarás el documento (por ejemplo, "mi_coleccion")
    nombre_coleccion = "results"
    collection=client[nombre_base_datos][nombre_coleccion]
    # Datos para el documento que insertarás en la colección
    results=[]
    documents=collection.find()
    for document in documents:
        results.append(document)
    
    # Cerrar la conexión
    client.close()
    return results

def getPrompt(prompt):
    client = MongoClient('localhost', 27017)

    # Nombre de la base de datos que deseas crear (por ejemplo, "mi_base_de_datos")
    nombre_base_datos = "results_chat"

    # Nombre de la colección donde insertarás el documento (por ejemplo, "mi_coleccion")
    nombre_coleccion = "results"
    collection=client[nombre_base_datos][nombre_coleccion]
    # Datos para el documento que insertarás en la colección
    result = collection.find_one({"_id":"dd6d3e2-794f-4321-95dc-97821374f0d4"})
    if result:
        print("Documento encontrado:")
        print(result)
    else:
        print("Documento no encontrado.")
    # Cerrar la conexión
    client.close()
    return result
