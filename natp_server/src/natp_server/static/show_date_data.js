$(document).ready(function(){
    $(".data_table").hide();
    $(".data_table_d").hide();
    $(".data_table_f").click(function(){
        $(".data_table").toggle();
        $(".data_table_d").toggle();
    });
});
