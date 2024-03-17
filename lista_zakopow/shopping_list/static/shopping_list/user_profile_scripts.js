import { show_error_popup } from "./show_error_popup.js";


window.addEventListener("load", (event) => { 
    add_listener_to_create_new_list();
    if(document.getElementById("div_error_flag_error_popup")!= null)
    {
        show_error_popup();
    }
});

function add_listener_to_create_new_list()
{
    document.getElementById("create_new_list_button").addEventListener("click", (event) => {
        if(document.getElementById("new_list_name").value === "" )
        {
            show_error_popup("Podaj nazwę nowej listy");
        }
        else
        {
            document.getElementById("create_new_list_form_id").submit();
        }
    });
}




