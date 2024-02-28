
select = document.getElementsByName("category")[0];
category = select.options;

form = document.getElementsByName("search_form")[0];

form.onkeypress = (e) => {
    const key = e.keyCode || e.charCode || 0;
    if (key == 13 && select.selectedIndex < 2) {
        category[1].selected = true;
    }
}
