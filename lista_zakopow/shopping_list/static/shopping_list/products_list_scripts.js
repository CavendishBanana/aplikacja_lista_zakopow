//import { show_error_popup } from "./show_error_popup.js";

window.addEventListener("load", (event) => { 
    add_listener_to_delete_list();
    add_listener_to_add_new_product();
    //periodicRefresh();

});

function add_listener_to_add_new_product()
{
    document.getElementById("add_new_product_button_id").addEventListener("click", (event) => {
        let new_product_description = document.getElementById("new_product_name");
        if(new_product_description.value === "")
        {
            show_error_popup("Podaj nazwę produktu");
        }
        else
        {
            document.getElementById("add_new_product_form_id").submit();
        }
    });
    
}



function add_listener_to_delete_list()
{
    delete_list_button = document.getElementById("delete_list_button_id");
    delete_list_button.addEventListener("click", (event) => {
        if(window.confirm("Czy na pewno chcesz skasować listę?"))
            {
                document.getElementById("delete_list_form_id").submit();
            }
    });
    
}

function periodicRefresh()
{
    console.log("periodicRefresh");
    let refresh_url = getCookie("referesh_link_lista_zakopow");
    console.log(refresh_url);
    setInterval(  () => {
        refreshProductsTable(refresh_url);
    }, 120000);

}

function refreshProductsTable(refresh_url)
{  
    fetch(refresh_url).then(response => console.log(response) )
        /*.then( data => { 
        if(data.status === "ok")
        {
            console.log("refreshProductsTable");
            items = data.items;
            for( let i =0; i< items.lenthg; i++)
            {
                console.log(items["item_description"]);
            }
        }

    } )*/
}

