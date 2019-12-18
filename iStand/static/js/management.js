$(function(){
  $.get('/search/').done(function(data){
    console.log(data);
    $("#book_list").append(data['data'])
  });

  //フォームが送信されたときのイベント
  $('#search_form').on('submit', function(e){
    e.preventDefault();
    var formData = new FormData($(this).get(0));
    var url = '/search/';
    $.ajax({
      type: 'GET',
      url: url,
      data: formData,
      processData: false,
      dataType: "json",
      contentType: false
    })
    .done(function(data){
      console.log(data)
    })
    .fail(function(){
      console.log('Ajax Error')
    });
  });
});
