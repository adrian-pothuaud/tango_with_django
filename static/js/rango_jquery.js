$(document).ready(function() {
    // JQuery code to be added in here.
    console.log("Page is Ready for jQuery !")

    $("#about-btn").click( function(event) {
        alert("You clicked the button using JQuery!");
    });

    $("p").hover( function() {
        $(this).css('color', 'red');
    },
    function() {
        $(this).css('color', 'black');
    });
});