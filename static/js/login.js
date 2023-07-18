document.addEventListener('DOMContentLoaded', function() {
    var formulario = document.getElementById('login-form');
    const apiUrl = "http://34.68.223.245:8000";
    formulario.addEventListener('submit', function(event) {
      event.preventDefault();
  
      var usernameInput = document.getElementById('username');
      var username = usernameInput.value;
      console.log(username)
      fetch(apiUrl+'/login', {
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
  