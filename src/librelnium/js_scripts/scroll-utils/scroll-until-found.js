window.scrollUntilFound = (scrollOne = null, scrollTwo = null, webElement, loopLimit = 15) => {
    const throwTypeError = (message) => {throw new TypeError(message)}
    
    if(scrollOne === null && scrollTwo === null){
        throwTypeError('Must pass an Element to either scrollOne or scrollTwo.')
    }

    if(scrollOne != null && scrollOne.nodeType != 1){
        throwTypeError(`Expected scrollOne to be a Element node or null, got ${typeof scrollOne}`)
    }

    if(scrollTwo != null && scrollTwo.nodeType != 1){
        throwTypeError(`Expected scrollTwo to be a Element node or null, got ${typeof scrollTwo}`)
    }

    if(webElement.nodeType != 1){
        throwTypeError(`Expected webElement to be Element node, got ${typeof webElement}`)
    }

    let count = 0;

    let id = setInterval(() => {
        let elementVisibility = webElement.checkVisibility();

        if(count === loopLimit || elementVisibility === true){            
            clearInterval(id);
        }

        if(scrollOne != null){
            scrollOne.scrollBy(100, 100);
        }

        if(scrollTwo != null){
            scrollTwo.scrollBy(100, 100);
        }
 
        count++;
    }, 500)
}