$(function(){
  //フォームが送信されたときのイベント
  $('#isbn_form').on('submit', function(e){
    e.preventDefault();
  });
  $('#isbn_form').on('change', function(e){
    e.preventDefault();

    $('#results').html("");
    $('#noresults').hide();

    //var formData = new FormData($(this).get(0));
    var isbn = $('[name=isbn]').val();
    if(isbn.length != 13){
      alert('13文字じゃないよ');
      return;
    }

    var data = {isbns : [isbn]};
    console.log(data);
    var url = '/isbn_to_info_as_html/';
    $.post({
      url: url,
      data: JSON.stringify(data),
      processData: false,
      dataType: "json",
      contentType: 'application/json'
    })
    .done(function(data){
      //console.log(data)
      if(!data['success']){
        console.log('Server Error');
        $('#results').html("");
        $('#noresults').show();
        return;
      }
      elem_results = $('#results');
      elem_results.html("")
      if(data['data'].length == 0){
        $('#results').html("");
        $('#noresults').show();
        return;
      }
      $('#noresults').hide();
      for(var i = 0; i < data['data'].length; i++){
        var elem = $($.parseHTML(data['data'][i]));
        elem_results.append(elem);
      }
      $("[name=add_button]").on('click', click_add);
    }).fail(function(){
      console.log('Ajax Error')
    });
  });

  var click_add = function(event){
    //イベント源のidを取得
    var button_id = event.target.id;
    //var id = parseInt(button_id.substr(4));
    var target_info = $("#book" + button_id.substr(4));
    //console.log(target_info);
    //formの作成
    var form = $('<form></form>', {
      name : 'book_form',
      method : 'POST',
      action : '/confirm_add/'
    });
    //isbnデータを格納するhidden要素を追加
    form.append(
      $('<input />', {
        type : 'hidden',
        name : 'title',
        value : target_info.find("[name=title]").html()
      }),
      $('<input />', {
        type : 'hidden',
        name : 'isbn',
        value : target_info.find("[name=isbn]").html()
      }),
      $('<input />', {
        type : 'hidden',
        name : 'authors',
        value : target_info.find("[name=authors]").html()
      }),
      $('<input />', {
        type : 'hidden',
        name : 'publisher',
        value : target_info.find("[name=publisher]").html()
      }),
      $('<input />', {
        type : 'hidden',
        name : 'thumbnail',
        value : target_info.find("[name=thumbnail]").attr("src")
      })
    );
    //ページに追加（送信するため）
    $("body").append(form);
    //console.log(form);
    //フォームを送信
    form.submit();
  };
});
