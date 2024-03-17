window.addEventListener("load", (event) => { 
    add_listener_to_delete_account_submit();
    if(document.getElementById("div_error_flag_error_popup")!= null)
    {
        show_error_popup();
    }

});

function add_listener_to_delete_account_submit(){
    
    let delete_account_button = document.getElementById("delete_account_button_id");
    delete_account_button.addEventListener("click", (event) => {
        console.log("delete account button clicked");
        console.log("password input value: " + document.getElementById("delete_account_password_submit").getAttribute("value") );
        if(document.getElementById("delete_account_password_submit").value === "")
        {
            window.alert("Podaj hasło");
        }
        else if(confirm("Usunięcie konta jest nieodwracalne. Czy na pewno chcesz usunąć konto?"))
        {
            document.getElementById("delete_account_form_id").submit();
        }
    });


}