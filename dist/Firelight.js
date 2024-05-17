"use strict";
var fileSelector = document.getElementById('file-selector');
if (fileSelector instanceof HTMLInputElement) {
    fileSelector.addEventListener('change', handleJSON());
}
else {
    console.error('file-selector is not a input element');
}
function handleJSON(ev) {
    var inputElement = ev.currentTarget;
    var fileList = inputElement.files;
    console.log(fileList);
}
