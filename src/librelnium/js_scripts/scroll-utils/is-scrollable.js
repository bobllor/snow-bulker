window.isScrollable = (element = null) => {
    let elt = element != null ? element : document.body;

    let overflowValue = window.getComputedStyle(elt).getPropertyValue('overflow');

    return overflowValue != 'hidden' ? true : false;
}