$(function(){
  var isFirst = true;
  var search = function(query){
    var get = {'query' : query};
    $.get('/search/', get).done(function(data){
      console.log(data);
      $("#book_list").text("");
      $("#book_list").append(data['data']);

      if(isFirst && $("#book_list")[0].childNodes.length == 0){
        console.log('a');
        $('.mng_nobook').show();
      }
      isFirst = false;

      //ボタンが押されたときのイベント
      $('[name=pickup]').off('click');
      $('[name=pickup]').on('click', function(e){
        id = e.target.id.substr(6);
        //console.log(id);
        pickup(id);
      });

      $('[name=book]').off('click');
      $('[name=book]').on('click', function(e){
        id = e.currentTarget.id.substr(4);
        if(e.target.type=='button'){
          return;
        }
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
          $("#detail_overflow").addClass("detail_overflow");
          $("#zone_detail").addClass("zone_detail");

          //詳細の閉じるボタン
          //$("#detail_overflow").hide();
          $("#close").on('click', function(e){
            //$("#detail_overflow").hide();
            console.log("close");
            $("#detail_overflow").removeClass("detail_overflow");
            $("#zone_detail").removeClass("zone_detail");
          });

          $("#pickup").on('click', function(e){
            id = $("#bookid").val();
            //console.log(id);
            pickup(id);
          });
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
    //console.log(id);
  }

  //本の追加ページへ遷移
  $('#mng_nobook_add').on('click', function(e){
    console.log('hello');
    window.location.href = "/additional/";
  });
});
