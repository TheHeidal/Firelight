const fileSelector = document.getElementById('file-selector');

function handleJSON(ev: Event): void {
    const inputElement = ev.currentTarget as HTMLInputElement;
    const fileList = inputElement.files;
    console.log(fileList);

}

if (fileSelector instanceof HTMLInputElement) {
    fileSelector.addEventListener('change', handleJSON);
} else {
    console.error('file-selector is not a input element')
}


