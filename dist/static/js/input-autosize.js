//textareaの要素を取得
let textarea = document.querySelectorAll('.input1');

//textareaのinputイベント
textarea.forEach(function(input_data) {
    //textareaのデフォルトの要素の幅を取得
    let clientWidth = input_data.clientWidth;

    input_data.addEventListener('input', ()=>{
        //textareaの要素の幅を設定（rows属性で行を指定するなら「px」ではなく「auto」で良いかも！）
        input_data.style.width = clientWidth + 'px';
        //textareaの入力内容の幅を取得
        let scrollWidth = input_data.scrollWidth;
        //textareaの幅に入力内容の幅を設定
        input_data.style.width = scrollWidth + 'px';
    });
});
