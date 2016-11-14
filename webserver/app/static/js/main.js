function reshape(el, id) {
    var elcabs = document.getElementById(id);
    var disp = window.getComputedStyle(elcabs).getPropertyValue('display');

    if (disp != "none") {
        elcabs.style["display"] = "none";
        el.innerHTML = "ABSTRACT &or;"
    } else {
        elcabs.style["display"] = "block";
        el.innerHTML = "ABSTRACT &and;"
    }
}
