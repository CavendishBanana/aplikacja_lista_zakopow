window.addEventListener("load", (event) => { 
    add_listener_to_create_new_list();

});

function add_listener_to_create_new_list()
{
    document.getElementById("create_new_list_button").addEventListener("click", (event) => {
        if(document.getElementById("new_list_name").value === "a" || document.getElementById("div_error_flag_error_popup") != null )
        {
            if( document.getElementById("div_error_flag_error_popup") != null )
            {document.getElementById("div_error_flag_error_popup").remove();}
            let error_popup_box = document.getElementById("error_popup");

            let err_p_tag = document.getElementById("error_msg_p");
            //error_popup_box.style.backgroundColor ="lightcoral";
            err_p_tag.innerHTML = "Podaj nazwę nowej listy";
            err_p_tag.style.backcolor= "lightcoral";
            err_p_tag.style.color="black";
            let visible_value="block";
            //error_popup_box.style.display = visible_value; 
            setTimeout(() => {
                //error_popup_box.setAttribute(invisible_property, invisible_value);    
                //error_popup_box.style.display = invisible_value; 
                //err_p_tag.style.color = "white";
                err_p_tag.innerHTML = "a";
                err_p_tag.style.backcolor= "white";
                err_p_tag.style.color= "white";
                
                //error_popup_box.style.backgroundColor ="white";
              }, 3000);
        }
        else
        {
            document.getElementById("create_new_list_form_id").submit();
        }
    });
}




