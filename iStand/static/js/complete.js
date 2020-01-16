$(function(){
  // [isCompletedBlock, isCompletedSonicSensor, isFinished]
  var state = [null, null, null];
  var getState = function(data){
    //引数があるか
    if(data != null){
      //通信が成功
      if(data['success']){
        //要素が変化したかを調べる
        flag = true;
        for(var i = 0; i < state.length; i++){
          flag = flag && (state[i] == data['data'][i]);
        }
        // 状態の更新
        state = data['data'];
        console.log(state);
        // 要素に変化があったら
        if(!flag){
          console.log('change');
          //moving
          if(state[2]) complete(state[1]);
          else if(!state[0]) moving();
          else if(state[0]) stop();
        }
      }
      if(!state[2]){
        $.getJSON("/get_state/", getState);
      }
    }
  }

  var elem_moving = $('#moving');
  var elem_stop = $('#stop');
  var elem_complete = $('#complete');

  elem_moving.hide();
  elem_stop.hide();
  elem_complete.hide();

  getState(state);
  // 移動中
  var moving = function(){
    elem_moving.show();
  }
  // 移動完了！収納してねor取り出してね
  var stop = function(){
    elem_stop.show();
  }
  // 収納or取り出し完了！ホームに戻ろうか
  var complete = function(isCompletedSonicSensor){
    // 収納or取り出し完了をサーバに通知
    var op = $('#operation').val();
    var url = "/update_book/";
    var data = {
      operation : $('#operation').val(),
      book_id : $('#book_id').val(),
      block_id : $('#block_id').val()
    };

    $.post({
      url: url,
      data: JSON.stringify(data),
      dataType: "json",
      contentType: 'application/json'
    }).done(function(data){
      console.log(data);
    });

    elem_complete.show();
    console.log(isCompletedSonicSensor);
  }
});
