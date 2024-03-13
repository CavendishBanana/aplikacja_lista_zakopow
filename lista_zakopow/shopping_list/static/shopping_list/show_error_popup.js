function show_error_popup(err_msg="", display_duration=3000)
{
    let error_popup_box = document.getElementById("error_popup");

    let err_p_tag = document.getElementById("error_msg_p");
    if(err_p_tag.innerHTML.length != 0)
    {
        err_p_tag.innerHTML = err_msg;
    }
    err_p_tag.style.backgroundColor= "lightcoral";
    err_p_tag.style.color="black";
    if(err_p_tag.length === 0)
    {
        err_p_tag.innerHTML = err_msg;
    }
    let visible_value="block";
    error_popup_box.style.display = visible_value; 
    setTimeout(() => {
        //error_popup_box.setAttribute(invisible_property, invisible_value);    
        //error_popup_box.style.display = invisible_value; 
        //err_p_tag.style.color = "white";
        console.log( document.getElementById("error_msg_p").innerHTML);
        err_p_tag.innerHTML = "a";
        err_p_tag.style.color= "white";
        err_p_tag.style.backgroundColor= "white";
        error_popup_box.style.backgroundColor ="white";
        }, 3000);

}

//export { show_error_popup };