window.addEventListener("load", (event) => {
    console.log("main page script");
    let error_popup_box = document.getElementById("error_popup");
    if(error_popup_box != null)
    {
        let err_p_tag = document.getElementById("error_msg_p");
        //let invisible_property = "display";
        let invisible_value="none";
        let visible_value="block";
        console.log("main page script 2");
        console.log(error_popup_box);
        //modal.style.display = "block";
        error_popup_box.style.display = visible_value; 
        //error_popup_box.setAttribute(invisible_property, visible_value);
        setTimeout(() => {
            //error_popup_box.setAttribute(invisible_property, invisible_value);    
            //error_popup_box.style.display = invisible_value; 
            //err_p_tag.style.color = "white";
            console.log( document.getElementById("error_msg_p").innerHTML);
            err_p_tag.innerHTML = "a";
            err_p_tag.style.color= "white";
            error_popup_box.style.backgroundColor ="white";
          }, 3000);
        prepareCookiesHandling();
    }

  });


  function getCookie(cName) {
    const name = cName + "=";
    const cDecoded = decodeURIComponent(document.cookie); 
    const cArr = cDecoded.split('; ');
    let res = null;
    cArr.forEach(val => {
      if (val.indexOf(name) === 0) res = val.substring(name.length);
    })
    return res;
  }

  function prepareCookiesHandling(){
        let cookies_policy_accept_cookie = getCookie("lista_zakopow_accept_cookies");
        if(cookies_policy_accept_cookie != null)
        {
            let cookiesPopupContainer = document.getElementById("simple-cookie-consent");
            if( cookiesPopupContainer != null) 
            {cookiesPopupContainer.remove();}
        }
        else
        {
            let cookiesPopupContainer = document.getElementById("simple-cookie-consent");
            document.getElementById("cookie-consent-button-id").addEventListener("click", (event) => 
            {
                document.cookie = "lista_zakopow_accept_cookies=1";
                cookiesPopupContainer.remove();
            })
        }
    }