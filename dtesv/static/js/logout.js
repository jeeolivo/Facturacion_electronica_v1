document.addEventListener("DOMContentLoaded", function() {
    var logoutLink = document.getElementById("logout-link");
    if (logoutLink) {
      logoutLink.addEventListener("click", function(event) {
        event.preventDefault();
  
        var form = document.createElement("form");
        form.setAttribute("method", "post");
        form.setAttribute("action", "/dtesv/home/");
  
        var csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
        form.innerHTML =
          '<input type="hidden" name="action" value="logout">' +
          '<input type="hidden" name="csrfmiddlewaretoken" value="' +
          csrfToken +
          '">';
  
        document.body.appendChild(form);
        form.submit();
      });
    }
  });
  