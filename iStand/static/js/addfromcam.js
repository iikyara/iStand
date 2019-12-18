$(function(){
  $('input[type=file]').after('<br><span></span>');

  // アップロードするファイルを選択
  $('input[type=file]').change(function() {
    var file = $(this).prop('files')[0];

    // 画像以外は処理を停止
    if (! file.type.match('image.*')) {
      // クリア
      $(this).val('');
      $('span').html('');
      return;
    }

    // 画像表示
    var reader = new FileReader();
    reader.onload = function() {
      var img_src = $('<img>').attr('src', reader.result);
      $('span').html(img_src);
    }
    reader.readAsDataURL(file);
  });

  //フォームが送信されたときのイベント
  $('#image_form').on('submit', function(e){
    e.preventDefault();
    var formData = new FormData($(this).get(0));
    var url = '/image_to_info_as_html/';
    $.ajax({
      type: 'POST',
      url: url,
      data: formData,
      processData: false,
      dataType: "json",
      contentType: false
    })
    .done(function(data){
      //console.log(data)
      if(!data['success']){
        console.log('Server Error');
        return;
      }
      elem_results = $('#results');
      elem_results.html("")
      if(data['data'].length == 0){
        elem_results.html("情報が見つかりませんでした");
        return;
      }
      for(var i = 0; i < data['data'].length; i++){
        var elem = $($.parseHTML(data['data'][i]));
        //console.log(elem);
        var button = $("<Button></Button>", {
          type : "button",
          name : "add_button",
          id : "add_" + String(i),
          html : "この情報で登録"
        });
        button.on('click', function(event){
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
              value : target_info.children("[name=title]").html()
            }),
            $('<input />', {
              type : 'hidden',
              name : 'isbn',
              value : target_info.children("[name=isbn]").html()
            }),
            $('<input />', {
              type : 'hidden',
              name : 'authors',
              value : target_info.children("[name=authors]").html()
            }),
            $('<input />', {
              type : 'hidden',
              name : 'publisher',
              value : target_info.children("[name=publisher]").html()
            }),
            $('<input />', {
              type : 'hidden',
              name : 'thumbnail',
              value : target_info.children("[name=thumbnail]").attr("src")
            })
          );
          //ページに追加（送信するため）
          $("body").append(form);
          //console.log(form);
          //フォームを送信
          form.submit();
        });
        elem.append(button);
        elem_results.append(elem);
      }
      /*
      data['data'].forEach(function(elem){
        console.log(elem);
        var node = $($.parseHTML(elem));
        $("<Button></Button>", {
          type : "button",
          name : "add_button",
          id : ""
        });
        elem_results.append(elem);
      });

      //formの作成
      var form = document.createElement('FORM');
      form.name = 'isbn_form';
      form.method = 'POST';
      form.action = '/confirm_add/';
      //isbnデータを格納するhidden要素を追加
      var isbn = document.createElement('input');
      isbn.type = 'hidden';
      isbn.name = 'isbn';
      isbn.value = JSON.stringify(data['data']);
      //formに追加
      form.appendChild(isbn);
      //ページに追加（送信するため）
      document.body.appendChild(form);
      //フォームを送信
      form.submit();


      $.post('/confirm_add/',
        data['data'],
        function(result){

        },
        "json"
      );
      */
    })
    .fail(function(){
      console.log('Ajax Error')
    });
  });
});
