document.addEventListener('DOMContentLoaded', function() {
    var formulario = document.getElementById('login-form');
  
    formulario.addEventListener('submit', function(event) {
      event.preventDefault();
  
      var usernameInput = document.getElementById('username');
      var username = usernameInput.value;
      console.log(username)
      fetch('http://127.0.0.1:8080/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })

      })
      .then(function(response) {
        if (response.redirected) {
          

            window.location.href = response.url;
        } else {
          console.log('Success:', response);
        }
      })
      .catch(function(error) {
        console.log('Error:', error);
      });
    });
  });
  