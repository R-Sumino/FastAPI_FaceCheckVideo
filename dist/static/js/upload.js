const buttonElement = document.getElementsByClassName("buttonUpload")[0]

buttonElement.addEventListener("click", () => {
  document.getElementsByName("files")[0].click();
});

// Space / Enter キーで click イベントを発火できるようにする
buttonElement.addEventListener("keydown", (event) => {
  if (!buttonElement.isEqualNode(event.target)) {
    return;
  }

  if (event.keyCode === 32 || event.keyCode === 13) {
    event.preventDefault();
    document.getElementsByName("files")[0].click();
  }
});



document.getElementsByName("files")[0].addEventListener('change', () => {
    const file_name = document.getElementsByName("files")[0].files
    var display_id = document.getElementById("filename_show")

    var list = ""
    for(var i = 0; i < file_name.length; i++){
        list += file_name[i].name + ", "
    }

    var result = list.substring(0, list.length-2);
    display_id.innerHTML = result;
    display_id.style.display = "inline-block";
})
