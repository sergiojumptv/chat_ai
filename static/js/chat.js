var saved_prompts = [];
var current_prompt=""
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
  var waiting=false
  get_prompts()
  function crearTabla(data) {
  var tabla = document.createElement('table');
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
    fetch(apiUrl+'/get_prompts', {
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
    fetch(apiUrl+'/clear_chats', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }

    })
      .then(response => {
        if (response.ok) {
          console.log('Conversaciones borradas exitosamente');
          get_prompts()
        } else {
          console.log('Hubo un error al borrar las conversaciones');

        }
        current_prompt=""
      })
      .catch(error => {
        console.log('Error de red:', error);
      })
  });

  messageInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      send_pressed();
    }
  });

  sendButton.addEventListener("click", function () {
    send_pressed()
  });

  function send_pressed(){
    console.log(waiting)
    if (current_prompt==""  && !waiting){
      if (saved_prompts.length==0){
      console.log("no prompts")
      

      savePrompt("Chat 1", function() {
        get_conversation_of_prompt("Chat 1", function() {
          seleccionarPrompt("Chat 1")
          sendMessage()
          waiting=false
        });
        
      });}
      else{
        get_conversation_of_prompt(saved_prompts[0], function() {
          console.log("cargando conver",saved_prompts[0])
          sendMessage()
          waiting=false
        });
      }
    }else if (!waiting){
      sendMessage();
      console.log("sending")
    }

  }



  mostrarTabla.addEventListener("click", function () {
    tablaContainer.style.display = 'block';

  })
  salirTabla.addEventListener("click", function () {
    tablaContainer.style.display = 'none';
  })
  function load_prompts() {
    
    listOfPrompts.innerHTML = ""
    const button_new_prompt=document.createElement("button");
      button_new_prompt.classList.add("prompt");
      button_new_prompt.setAttribute("button","save");
      button_new_prompt.id = "save-button";


    const img_new_prompt=document.createElement("img");
      img_new_prompt.src="/static/images/nuevo_prompt.png"
      img_new_prompt.style.width = '20px'; 
      img_new_prompt.style.height = '20px';

    const text_new_prompt=document.createElement("span");
      text_new_prompt.textContent = "Nuevo Chat";
      text_new_prompt.style.marginLeft='5px';
    
    button_new_prompt.appendChild(img_new_prompt);
    button_new_prompt.appendChild(text_new_prompt);
    button_new_prompt.addEventListener("click", function () {

      const name = prompt("Ingrese un nombre:");
      
      if (name) {
        savePrompt(name);
      }
    });
    listOfPrompts.appendChild(button_new_prompt);
    saved_prompts.forEach(item => {

      console.log("Nombre guardado:", item);
      const prompt = document.createElement("button");
      prompt.id = "prompt";


      const img_msg=document.createElement("img");
        img_msg.src="/static/images/mensaje.png"
        img_msg.style.width = '20px'; 
        img_msg.style.height = '20px';

      const text_prompt=document.createElement("span");
        text_prompt.textContent = item;
        text_prompt.style.marginLeft='5px';
      
      prompt.classList.add("prompt");
      prompt.appendChild(img_msg);
      prompt.appendChild(text_prompt);
      prompt.addEventListener("click", function () {
        get_conversation_of_prompt(prompt.textContent);
        console.log(prompt.textContent);
      });
      
      listOfPrompts.appendChild(prompt);



    });

  }

  function sendMessage() {
    const message = messageInput.value.trim();
    if (message=="") console.log("mensaje vacio")
    else{
    fetch(apiUrl+'/generate_uuid', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
      .then(data => {
        
        uuid_gen=data.uuid

          const messageUser = {
            author: "user",
            content: message,
            uuid:uuid_gen
            
          }
          include_msg(messageUser)

              

       // URL de la API

      const body_dict = {
        text: message,
        uuid:uuid_gen
      };

      fetch(apiUrl+'/send_message', {
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
  }

  function savePrompt(name, callback) {
 // URL de la API para guardar el nombre
    waiting=true
    const data = {
      name: name
    };

    fetch(apiUrl+'/save-prompt', {
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
        current_prompt=name
        if (callback && typeof callback === 'function') {
          callback();
        }
      })
      .catch(error => {
        console.error("Error:", error);
      });

  }
  function get_conversation_of_prompt(name,callback) {
    current_prompt=name


    const data = {
      name: name
    };

    fetch(apiUrl+"/get_conversation_of_prompt", {
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
        seleccionarPrompt(name)
      
        if (callback && typeof callback === 'function') {
          callback();
        }
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
      dislikeButton.classList.add("button-dislike")
      likeButton.style.float="inline-end"
      dislikeButton.style.float="inline-start"
      buttonsContainer.classList.add("like");
      if ("feedback" in msg){
        if (msg["feedback"] =="like"){
          select_like(likeButton,dislikeButton,"like")
        }else if (msg["feedback"]=="dislike"){
          select_like(likeButton,dislikeButton,"dislike")
        }
      }
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
    
    console.log("uuid= ",msg["uuid"])
    chatMessages.appendChild(replyElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  function seleccionarPrompt(name) {
    // Obtener todos los divs con la clase "inner-div"
    var divs = document.querySelectorAll(".prompt");

    // Recorrer todos los divs y quitar la clase "selected" para eliminar el borde negro
    divs.forEach(function(item) {
      console.log(item.children[1].textContent, ' ', name)
        if (item.children[1].textContent == name)
          item.setAttribute("selected","True");
        else
          item.setAttribute("selected","False");
        
    });

    // Aplicar la clase "selected" solo al div que fue clickeado

}
});

