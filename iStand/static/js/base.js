$(function(){
  var blueset = [
    "#112342", // 0
    "#507DBC", // 1
    "#A1C6EA", // 2
    "#BBD1EA", // 3
    "#EAEFF0", // 4
    "#FFFFFF", // 5
    "#AAAAAA", // 6
    "#050505"  // 7
  ];

  var colors = blueset;

  // 背景色設定
  var background = [
    {elem : $("body"), color:colors[5]},
    {elem : $(".base_menu"), color:colors[5]},
    {elem : $(".long_button"), color:colors[5]}
  ];

  // 文字色設定
  var font = [
    {elem : $("body"), color:colors[7]},
    {elem : $("h1"), color:colors[0]},
    {elem : $("h1"), color:colors[0]},
    {elem : $(".base_menu a"), color:colors[2]},
    {elem : $(".base_head_description"), color:colors[1]},
    {elem : $(".base_head_description i"), color:colors[3]},
    {elem : $("#button_addfromcam, #button_addfromisbn"), color:colors[7]}
  ];

  var other = [
    {elem : $(".base_menu"), color:colors[4], css:"border-color"},
    {elem : $(".base_head_line"), color:colors[4], css:"border-color"}
  ];

  background.forEach(v => v.elem.css('background-color', v.color));
  font.forEach(v => v.elem.css('color', v.color));
  other.forEach(v => v.elem.css(v.css, v.color));

  //表示中のページに応じてメニューを濃くする．
  var pages = [
    {name:"ホーム", id:"#menu_home"},
    {name:"取り出し", id:"#menu_management"},
    {name:"追加", id:"#menu_additional"}
  ];
  var title = $('title').text();
  pages.forEach(function(page){
    if(title.includes(page.name)){
      $(page.id).css('color', colors[0]);
    }
  });
});

window.onpageshow = function(event) {
  if (event.persisted) {
    window.location.reload()
  }
};

/**
* タッチ操作での拡大縮小禁止
*/
document.addEventListener("touchmove", mobile_no_scroll, { passive: false });
/**
* 拡大縮小禁止
*/
function mobile_no_scroll(event) {
    // ２本指での操作の場合
    if (event.touches.length >= 2) {
        // デフォルトの動作をさせない
        event.preventDefault();
    }
}
