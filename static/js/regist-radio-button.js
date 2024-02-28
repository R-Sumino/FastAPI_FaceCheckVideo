function formSwitch() {
    check = document.getElementsByClassName('js-check')
    var web = document.getElementById('device');
    var ip = document.getElementById('ipcam');
    if (check[0].checked) {
        // Webカメラが選択されたら下記を実行します
        document.getElementById('Web-id').style.display = "inline-block";
        web.required = true;
        document.getElementById('IP-id').style.display = "none";
        ip.required = false;
        
    } else if (check[1].checked) {
        // IPカメラが選択されたら下記を実行します
        document.getElementById('Web-id').style.display = "none";
        web.required = false;
        document.getElementById('IP-id').style.display = "inline-block";
        ip.required = true;
    } else {
        document.getElementById('Web-id').style.display = "none";
        web.required = false;
        document.getElementById('IP-id').style.display = "none";
        ip.required = false;
    }
}
window.addEventListener('load', formSwitch());

