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
    elem_moving.fadeIn(500);
    $('#point1').addClass("progressbar_point_now");
  }
  // 移動完了！収納してねor取り出してね
  var stop = function(){
    //moving();

    $('#point1').removeClass("progressbar_point_now");
    $('#point1').addClass("progressbar_point_check");
    $('#point2').addClass("progressbar_point_now");
    $('#line1-2').addClass("progressbar_line_check");

    var data = {
      block_id : $('#block_id').val()
    };
    $.post({
      url : '/get_block_position/',
      data : JSON.stringify(data),
      dataType : 'json',
      contentType : 'application/json'
    }).done(function(data){
      console.log(data);
      var block = $('#block' + data['data'])
      block.addClass("block_selected");
      block.text("ココ");
      elem_moving.fadeOut(500);
      elem_stop.fadeIn(500);
    });
  }
  // 収納or取り出し完了！ホームに戻ろうか
  var complete = function(isCompletedSonicSensor){
    //moving();
    //stop();
    $('#point1').removeClass("progressbar_point_now");
    $('#point1').addClass("progressbar_point_check");
    $('#point2').removeClass("progressbar_point_now");
    $('#point2').addClass("progressbar_point_check");
    $('#point3').addClass("progressbar_point_now");
    $('#line2-3').addClass("progressbar_line_check");
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

    elem_moving.fadeOut(500);
    elem_stop.fadeOut(500);
    elem_complete.fadeIn(500);
    console.log(isCompletedSonicSensor);
  }
});
