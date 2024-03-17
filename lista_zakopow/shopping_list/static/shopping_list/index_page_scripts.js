import { show_error_popup } from "./show_error_popup.js";

window.addEventListener("load", (event) => {
    console.log("main page script");
    if( document.getElementById("div_error_flag_error_popup") != null )
    {
      console.log("load page event - error flag set");
      show_error_popup();
    }

    prepareCookiesHandling();
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