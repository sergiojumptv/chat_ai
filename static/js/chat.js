let saved_prompts = [];

document.addEventListener("DOMContentLoaded", function () {
  const chatMessages = document.getElementById("chat-messages");
  const messageInput = document.getElementById("message-input");
  const sendButton = document.getElementById("send-button");
  const listOfPrompts = document.getElementById("chat_prompts")
  const saveButton = document.getElementById("save-button");
  const clearChats = document.getElementById("clear-chats")
  const mostrarTabla = document.getElementById("mostrarTabla")
  const salirTabla = document.getElementById("salir-tabla")
  const tablaContainer = document.getElementById('tabla-container');
  const apiUrl = "http://127.0.0.1:8000";
  get_prompts()
  get_conversation_of_prompt("default_prompt")
  function crearTabla(data) {
  var tabla = document.createElement('table');
  current_prompt=""
  // Crear el encabezado de la tabla
  var encabezado = tabla.createTHead();
  var filaEncabezado = encabezado.insertRow();
  

  // Crear las filas de datos
  var cuerpo = tabla.createTBody();
  for (var i = 0; i < data.length; i++) {
    var fila = cuerpo.insertRow();
    for (var j = 0; j < data[i].length; j++) {
      var celda = fila.insertCell();
      celda.textContent = data[i][j];
    }
  }

  // Agregar la tabla al documento
  var tablaR = tablaContainer.querySelector('table');
  if (tablaR){
    tablaContainer.removeChild(tablaR)
  }
  
  tablaContainer.appendChild(tabla);
  const celdas = document.querySelectorAll('#tabla-container td');

// Recorrer todas las celdas y aplicar estilos según su contenido
celdas.forEach(celda => {
  const contenido = celda.textContent.trim();
  
  // Verificar si el contenido es un número
  if (!isNaN(contenido)) {
    celda.style.textAlign = 'right'; // Alinear a la derecha para números
  } else {
    celda.style.textAlign = 'left'; // Alinear a la izquierda para otros contenidos
  }
});
}

  
  function give_feedback(feedback,uuid_gen){
    const data = {
      prompt: current_prompt,
      uuid: uuid_gen,
      feedback: feedback
    };
    
    fetch(apiUrl+'/give_feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    }).then(response => {
      if (response.ok) {
        console.log('Solicitud POST exitosa');
      } else {
        throw new Error('Error en la respuesta del servidor');
      }
    }).catch(error => {
      console.error('Error en la petición:', error);
    });
    
  }
  function get_prompts() {
    fetch('http://127.0.0.1:8000/get_prompts', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Error en la respuesta de la API');
      })
      .then(data => {

        // El array de respuesta está almacenado en la variable 'data'
        console.log(data)
        saved_prompts = data
        load_prompts()
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }

  clearChats.addEventListener("click", function () {
    fetch('http://127.0.0.1:8000/clear_chats', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }

    })
      .then(response => {
        if (response.ok) {
          console.log('Conversaciones borradas exitosamente');
          get_prompts()
          get_conversation_of_prompt('default_prompt')
        } else {
          console.log('Hubo un error al borrar las conversaciones');
        }
      })
      .catch(error => {
        console.log('Error de red:', error);
      })
  });

  sendButton.addEventListener("click", function () {
    sendMessage();
  });

  saveButton.addEventListener("click", function () {
    const name = prompt("Ingrese un nombre:");

    if (name) {
      savePrompt(name);
    }
  });

  mostrarTabla.addEventListener("click", function () {
    tablaContainer.style.display = 'block';

  })
  salirTabla.addEventListener("click", function () {
    tablaContainer.style.display = 'none';
  })
  function load_prompts() {
    listOfPrompts.innerHTML = ""
    saved_prompts.forEach(item => {

      console.log("Nombre guardado:", item);
      const prompt = document.createElement("button");
      prompt.id = "prompt"
      prompt.textContent = item;
      prompt.classList.add("prompt")

      prompt.addEventListener("click", function () {
        get_conversation_of_prompt(prompt.textContent)
        console.log(prompt.textContent)
      });
      
      listOfPrompts.appendChild(prompt);



    });
  }

  function sendMessage() {
    const message = messageInput.value.trim();
    fetch('/generate_uuid')
      .then(response => response.json())
      .then(data => {
        
        uuid_gen=data.uuid
        if (message !== "") {
          const messageUser = {
            author: "user",
            content: message,
            uuid:uuid_gen
            
          }
          include_msg(messageUser)
        }
              

       // URL de la API

      const body_dict = {
        text: message,
        uuid:uuid_gen
      };

      fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body_dict)
      })
        .then(response => {
          if (response.ok) {
            return response.json();
          }
          throw new Error("Error en la respuesta de la API");
        })
        .then(responseData => {
          console.log(responseData)
          if ('result' in responseData) {
            include_msg({ author: "bot", content: responseData.reply, result: responseData.result, uuid:responseData.uuid })}
          else { include_msg({author: "bot",content: responseData.reply,uuid:responseData.uuid})}

        })
        .catch(error => {
          console.error("Error:", error);
        });

      messageInput.value = "";
      })
      .catch(error => {
        console.error('Error al obtener el UUID:', error);
      });
    
  }

  function savePrompt(name) {
    const apiUrl = "http://127.0.0.1:8000/save-prompt"; // URL de la API para guardar el nombre

    const data = {
      name: name
    };

    fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("Error en la respuesta de la API");
      })
      .then(responseData => {
        include_msg(responseData.reply)
        console.log("Nombre guardado exitosamente:", responseData);
        get_prompts()
      })
      .catch(error => {
        console.error("Error:", error);
      });
  }
  function get_conversation_of_prompt(name) {
    current_prompt=name
    const apiUrl = "http://127.0.0.1:8000/get_conversation_of_prompt"; // URL de la API para guardar el nombre

    const data = {
      name: name
    };

    fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
      .then(response => {
        
        if (response.ok) {
          return response.json();
        }
        throw new Error("Error en la respuesta de la API");
      })
      .then(data => {
        console.log("response -->",data)
        chatMessages.innerHTML = ""
        data.forEach(item => {
          console.log(item)
          include_msg(item)
        });
      })
      .catch(error => {
        console.error("Error:", error);
      });
  }

  function select_like(likeButton,dislikeButton,select){
    if (select=="like"){
    console.log("Me gusta");
        if (likeButton.style.opacity==1){
          dislikeButton.style.opacity="50%"
          likeButton.style.opacity="50%"
          likeButton.style.width="21px"
          dislikeButton.style.width="20px"
          give_feedback("",likeButton.id)
        }else{
        likeButton.style.opacity="100%"
        likeButton.style.width="23px"
        dislikeButton.style.width="17px"
        dislikeButton.style.opacity="20%"
        give_feedback("like",likeButton.id)
        }}
    else if (select=="dislike"){
      console.log("No me gusta");
        if (dislikeButton.style.opacity==1){
          dislikeButton.style.opacity="50%"
          likeButton.style.opacity="50%"
          likeButton.style.width="21px"
          dislikeButton.style.width="20px"
          give_feedback("",likeButton.id)
        }else{
          console.log(dislikeButton.style.opacity)
        likeButton.style.opacity="20%"
        likeButton.style.width="19px"
        dislikeButton.style.width="21px"
        dislikeButton.style.opacity="100%"
        give_feedback("dislike",likeButton.id)
        }

    }
  }
  function include_msg(msg) {
    const replyElement = document.createElement("div");
    replyElement.textContent = msg["content"];
    replyElement.classList.add("message");
    uuid_gen=msg["uuid"]
    replyElement.id = uuid_gen

    if (msg["author"] == "user") {
      replyElement.setAttribute("author", "user");
    } else if (msg["author"] == "bot") {
      replyElement.setAttribute("author", "bot");
  
      if ('result' in msg) {
        console.log("hay query");
        replyElement.setAttribute("select", "True");
  
        var tabla = msg['result'];
        replyElement.addEventListener("click", function(){
          tabla=msg['result'];
          crearTabla(tabla);
          tablaContainer.style.display = 'block';
        });
      } else {
        console.log("no hay query");
        console.log(msg);
      }
  
      // Crear contenedor para los botones
      const buttonsContainer = document.createElement("div");
  
      // Crear botones "Me gusta" y "No me gusta"
      
      const likeButton = document.createElement("img");
      likeButton.id=uuid_gen
      likeButton.src = "/static/images/like.png";
      const dislikeButton = document.createElement("img");
      dislikeButton.id=uuid_gen
      dislikeButton.src = "/static/images/dislike.png";
      likeButton.classList.add("button-like")
      dislikeButton.classList.add("button-like")
      likeButton.style.float="inline-end"
      dislikeButton.style.float="inline-start"
      buttonsContainer.classList.add("like");
  
      // Agregar eventos a los botones
      likeButton.addEventListener("click", function() {
        // Acciones cuando se hace clic en "Me gusta"
        select_like(likeButton,dislikeButton,"like")
      });
  
      dislikeButton.addEventListener("click", function() {
        // Acciones cuando se hace clic en "No me gusta"
        select_like(likeButton,dislikeButton,"dislike")
      });
  
      replyElement.addEventListener("mouseover", function() {
        console.log("over")
        if (dislikeButton.style.opacity==1){
          likeButton.style.width="19px"
          dislikeButton.style.width="21px"
        }else if(likeButton.style.opacity==1){
          likeButton.style.width="23px"
          dislikeButton.style.width="17px"
        }else{
        likeButton.style.width="21px"
        dislikeButton.style.width="20px"
        }
        buttonsContainer.style.visibility="visible"
        buttonsContainer.style.height="23px"
      });
  
      replyElement.addEventListener("mouseout", function() {
        console.log("out")
        likeButton.style.width="0"
        dislikeButton.style.width="0"
        buttonsContainer.style.visibility="hidden"
        buttonsContainer.style.height="0px"
        

      });
  
      // Agregar los botones al contenedor
      buttonsContainer.appendChild(dislikeButton);
      buttonsContainer.appendChild(likeButton);
      
  
      // Agregar el contenedor debajo del mensaje
      replyElement.appendChild(buttonsContainer);
      if (msg["feedback"]=="like"){
        console.log("hil")
      }

    }
    
    console.log(msg["uuid"])
    chatMessages.appendChild(replyElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
});
