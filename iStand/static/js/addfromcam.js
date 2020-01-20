$(function(){
  // アップロードするファイルを選択
  $('input[type=file]').change(function() {
    var file = $(this).prop('files')[0];

    // 画像以外は処理を停止
    if (! file.type.match('image.*')) {
      // クリア
      $(this).val('');
      return;
    }

    // 画像表示
    var reader = new FileReader();
    reader.onload = function() {
      var img_src = $('<img>').attr('src', reader.result);
      $('#image_selector-label').html(img_src);
    }
    reader.readAsDataURL(file);
  });

  //フォームが送信されたときのイベント
  $('#image_form').on('submit', function(e){
    e.preventDefault();
  });
  $('#image_form').change(function(e){
    e.preventDefault();

    $('#results').html("");
    $('#noresults').hide();

    var formData = new FormData($(this).get(0));
    var url = '/image_to_info_as_html/';
    $.ajax({
      type: 'POST',
      url: url,
      data: formData,
      processData: false,
      dataType: "json",
      contentType: false
    }).done(function(data){
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

  $('#image_selector-label').on('drop', function(e){
    e.preventDefault();
    $('#image_selector')[0].files = e.dataTransfer.files;
  });
});
