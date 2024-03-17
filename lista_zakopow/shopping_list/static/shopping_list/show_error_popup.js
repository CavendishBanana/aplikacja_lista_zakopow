function show_error_popup(err_msg="", display_duration=3000)
{   
    console.log("show error popup function")
    if( document.getElementById("div_error_flag_error_popup") != null )
    {document.getElementById("div_error_flag_error_popup").remove();}
    //let error_popup_box = document.getElementById("error_popup");
    

    let err_p_tag = document.getElementById("error_msg_p");
    if(err_msg != "")
    {
        err_p_tag.innerHTML = err_msg;
    }
    err_p_tag.classList.remove("err_popup_p_tag_deactivated");
    err_p_tag.classList.add("err_popup_p_tag_activated");

    setTimeout(() => {

        err_p_tag.innerHTML = "a";
        err_p_tag.classList.remove("err_popup_p_tag_activated");
        err_p_tag.classList.add("err_popup_p_tag_deactivated");
        }, display_duration);

}

export { show_error_popup };