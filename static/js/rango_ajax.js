$(document).ready(function() {

    $.get('/rango/suggest/', {suggestion: ''}, function(data){
        $('#cats').html(data);
    });

    console.log('AJAX script Ready !');

    $('#likes').click(function(){
        console.log('Like button clicked');
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like/', {category_id: catid}, function(data){
            console.log('data received');
            $('#like_count').html(data);
            $('#likes').hide();
            console.log('Like count updated, like button hidden');
        });
    });

    $('#suggestion').keyup(function(){
        console.log('looking for suggestions');
        var query;
        query = $(this).val();
        $.get('/rango/suggest/', {suggestion: query}, function(data){
            $('#cats').html(data);
        });
    });
});