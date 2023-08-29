document.addEventListener('DOMContentLoaded', function () {
  var formulario = document.getElementById('login-form');

  const IP_SERVER = config_data.FLASK_SERVER;
  const MYSQL_PORT = config_data.MYSQL_PORT;

  const apiUrl = "";
  formulario.addEventListener('submit', function (event) {
    event.preventDefault();

    var usernameInput = document.getElementById('username');
    var username = usernameInput.value;
    console.log(IP_SERVER)
    fetch(IP_SERVER+"/login", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: username })

    })
      .then(function (response) {
        if (response.redirected) {


          window.location.href = response.url;
        } else {
          console.log('Success:', response);
        }
      })
      .catch(function (error) {
        console.log('Error:', error);
      });
  });
});
