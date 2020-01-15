$(function(){
  var search = function(query){
    var get = {'query' : query};
    $.get('/search/', get).done(function(data){
      console.log(data);
      $("#book_list").append(data['data']);
      //ボタンが押されたときのイベント
      $('[name=pickup]').on('click', function(e){
        id = e.target.id;
        pickup(id);
      });

      $('[name=detail]').on('click', function(e){
        id = e.target.id.substr(6);
        data = { bookids : [id] };
        console.log(data);
        $.ajax({
          type: 'POST',
          url: '/bookid_to_info_as_html/',
          data: JSON.stringify(data),
          dataType: "json",
          contentType: 'application/json'
        }).done(function(data){
          console.log(data);
          $("#zone_detail").html(data["data"]);
          $("#bookid").val(id);
          $("#detail_overflow").show();
        });
      });
    });
  }

  search('');

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
      console.log(data);
    })
    .fail(function(){
      console.log('Ajax Error');
    });
  });

  //詳細の閉じるボタン
  $("#detail_overflow").hide();
  $("#close").on('click', function(){
    $("#detail_overflow").hide();
  });

  //本取り出しメソッド
  var pickup = function(id){
    //formの作成
    var form = $('<form></form>', {
      name : 'book_pickup_form',
      method : 'POST',
      action : '/pickup/'
    });
    //isbnデータを格納するhidden要素を追加
    form.append(
      $('<input />', {
        type : 'hidden',
        name : 'operation',
        value : 'pickup'
      }),
      $('<input />', {
        type : 'hidden',
        name : 'bookid',
        value : id
      })
    );
    //ページに追加（送信するため）
    $("body").append(form);
    //console.log(form);
    //フォームを送信
    form.submit();
  }
});
