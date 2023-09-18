function add_ajax_hrefs(){
        document.querySelectorAll('.add_pokemon').forEach(item => {
                item.setAttribute('href','#');
            })
    }
<!-- document.addEventListener("DOMContentLoaded", add_ajax_hrefs) -->

$('.add_pokemon').click(function(event){
    event.preventDefault();
    var pid;
    pid = $(this).attr("data-pid");
    $.ajax({
        type:"POST",
        url: "{% url 'users:add_pokemon' %}",
        data:{
             pokemon_id: pid,
             csrfmiddlewaretoken: '{{ csrf_token }}'
        },
         success: function( data )
        {
        $('#add_pokemon_'+ pid).hide();
        $('#remove_pokemon_' + pid).show();

        }
     })
     return false;
});

$('.remove_pokemon').click(function(event){
    event.preventDefault();
    var pid;
    pid = $(this).attr("data-pid");
    $.ajax({
        type:"POST",
        url: "{% url 'users:remove_pokemon' %}",
        data:{
             pokemon_id: pid,
             csrfmiddlewaretoken: '{{ csrf_token }}'
        },
         success: function( data )
        {
        $('#add_pokemon_'+ pid).show();
        $('#remove_pokemon_' + pid).hide();

        }
     })
     return false;
});
