window.findScrollableElement = (query = null, property) => {
    let queryType = query === null ? 'div' : query;

    let elements = document.querySelectorAll(queryType);
    const scrollStyles = new Set(['auto', 'scroll']);

    for(let i = 0; i < elements.length - 1; i++){
        let styles = window.getComputedStyle(elements[i]);

        let elementStyle = styles.getPropertyValue(property);

        let isScrollable = elements[i].scrollHeight > elements[i].clientHeight;

        if(scrollStyles.has(elementStyle) && isScrollable){
            return elements[i];
        }
    }

    return null;
}