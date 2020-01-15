$(function(){
  //ボタンが押されたときのイベント
  $('[name=blk_btn]').on('click', function(e){
    var id = e.target.id.substr(7);

    //formの作成
    var form = $('<form></form>', {
      name : 'book_form',
      method : 'POST',
      action : '/moving/'
    });
    //isbnデータを格納するhidden要素を追加
    form.append(
      $('<input />', {
        type : 'hidden',
        name : 'operation',
        value : 'add'
      }),
      $('<input />', {
        type : 'hidden',
        name : 'session',
        value : $("#session")[0].value
      }),
      $('<input />', {
        type : 'hidden',
        name : 'title',
        value : $("#title")[0].value
      }),
      $('<input />', {
        type : 'hidden',
        name : 'isbn',
        value : $("#isbn")[0].value
      }),
      $('<input />', {
        type : 'hidden',
        name : 'authors',
        value : $("#authors")[0].value
      }),
      $('<input />', {
        type : 'hidden',
        name : 'publisher',
        value : $("#publisher")[0].value
      }),
      $('<input />', {
        type : 'hidden',
        name : 'thumbnail',
        value : $("#thumbnail")[0].value
      }),
      $('<input />', {
        type : 'hidden',
        name : 'blockid',
        value : id
      })
    );
    //ページに追加（送信するため）
    $("body").append(form);
    //console.log(form);
    //フォームを送信
    form.submit();
  });
});
