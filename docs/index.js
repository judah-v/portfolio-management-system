for (img of document.images) {
    let orig_style = getComputedStyle(img)
    img.addEventListener('mouseover', expandImg)
    img.addEventListener('mouseout', revertImg)
    
}
function expandImg(){
    this.style.transition = '.25s'
    this.style.transform = 'scale(2)';
    this.style.zIndex = 1;
}
function revertImg(){
    this.style.transform = 'none';
    this.style.zIndex = -10;
}