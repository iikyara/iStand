$(function(){
  var elem_freq = $('#freq');
  var elem_duty = $('#duty');
  var elem_isRight = true;
  var isStop = true;

  var start = function(e){
    isStop = false;
    var target = "";
    var nontar = "";
    var isRight = true;
    if(e.target.id=="toggle_r"){
      target = "#toggle_r";
      nontar = "#toggle_l";
      isRight = true;
      elem_isRight = true;
    }
    else{
      target = "#toggle_l";
      nontar = "#toggle_r";
      isRight = false;
      elem_isRight = false;
    }

    //モーターをスタートさせる
    data = {
      freq : elem_freq.val(),
      duty : elem_duty.val(),
      isRight : isRight
    }
    $.post({
      url: "/start_motor/",        // POST送信先のURL
      data: JSON.stringify(data),  // JSONデータ本体
      contentType: 'application/json', // リクエストの Content-Type
      dataType: "json",           // レスポンスをJSONとしてパースする
      success: function(data) {   // 200 OK時
        console.log(data);
        $(nontar).prop('disabled', true);
        $(target).text('ストップ');
        //$(target).onclick = "";
        $(target).off('click');
        $(target).on('click', stop);

      },
      error: function() {         // HTTPエラー時
        alert("Server Error. Pleasy try again later.");
      }
    });
  };

  var stop = function(e){
    isStop = true;
    var target = "";
    var nontar = "";
    if(e.target.id=="toggle_r"){
      target = "#toggle_r";
      nontar = "#toggle_l";
      isRight = true;
    }
    else{
      target = "#toggle_l";
      nontar = "#toggle_r";
      isRight = false;
    }

    //モーターをスタートさせる
    data = {
      freq : elem_freq.val(),
      duty : elem_duty.val(),
      isRight : isRight
    }
    $.post({
      url: "/stop_motor/",        // POST送信先のURL
      data: JSON.stringify(data),  // JSONデータ本体
      contentType: 'application/json', // リクエストの Content-Type
      dataType: "json",           // レスポンスをJSONとしてパースする
      success: function(data) {   // 200 OK時
        console.log(data);
        $(nontar).prop('disabled', false);
        $(target).text('スタート');
        //$(target).onclick = "";
        $(target).off('click');
        $(target).on('click', start);
      },
      error: function() {         // HTTPエラー時
        alert("Server Error. Pleasy try again later.");
      }
    });
  };

var change = function(e){
if(isStop){
 return;
}
console.log('a');
data = {
freq : elem_freq.val(),
duty : elem_duty.val(),
isRight: elem_isRight
};
$.post({
url: '/set_freq_and_duty/',
data: JSON.stringify(data),
dataType: 'json',
contentType: 'application/json'
}).done(function(data){
console.log(data)
});
};

elem_freq.on('change', change);
elem_duty.on('change', change);

  $('#toggle_r').on('click', start);
  $('#toggle_l').on('click', start);

  var elem_second = $('#second');
  var elem_num = $('#num');
  $('#save').on('click', function(e){
    console.log('a');
    var s = elem_second.val();
    var n = elem_num.val();
    speed = 360 * n / s;
    data = {
      freq : elem_freq.val(),
      duty : elem_duty.val(),
      speed : speed
    };
    $.post({
      url: "/upload_motor_data/",        // POST送信先のURL
      data: JSON.stringify(data),  // JSONデータ本体
      contentType: 'application/json', // リクエストの Content-Type
      dataType: "json",           // レスポンスをJSONとしてパースする
      success: function(data) {   // 200 OK時
        console.log(data);
      },
      error: function() {         // HTTPエラー時
        alert("Server Error. Pleasy try again later.");
      }
    });
  });
});
