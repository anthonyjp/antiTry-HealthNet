/**
 * Created by Matthew on 2/27/2016.
 */

var registry = {};
registry['base'] = (function (lodash, jQuery) {
    var curActive = null;

    /**
     * A utility function that checks if some element is inside a given indexable/sequential object, i.e. an object defined
     * by Lodash to be an ArrayLikeObject. If either is null/undefined or 'arr' is not an ArrayLikeObject then a TypeError
     * is thrown.
     *
     * Internally it simply uses lodash#some to determine truthiness.
     *
     * @param {Any} elem Element to look for
     * @param  {Array|Object} arr Array/Array-Like Object to look through
     * @returns {boolean} Whether or not the element exists in the given arr
     */
    function inArray(elem, arr) {
        if (lodash.isNil(elem) || lodash.isNil(arr) || !lodash.isArrayLikeObject(arr))
            throw new TypeError('inArray expects non-nil element and non-nil array-like (iterable)!');

        return lodash.some(arr, function (x) {
            return x === elem;
        });
    }

    /**
     * Sets the active .hn-menuitem in the navbar based on a simple command syntax. The string is formatted as the labels of the
     * buttons with pipes ('|') separating them.
     *
     * i.e. 'Log In|Home|About' would check against all .hn-item elements until the label matches 'Log In', 'Home' or 'About'. This is done
     * sequentially, so the first element to match any of those three strings is set to the new active item.
     *
     * @param {string} html_content The Button Label
     * @returns {boolean} True if succeeded, False otherwise
     */
    function setActiveMenuitem(html_content) {
        if (lodash.isNil(html_content) || !lodash.isString(html_content))
            return false;

        var options = lodash.trim(html_content).split('|');
        var newActive = jQuery('li.hn-menuitem > a').filter(function () {
            return inArray(this.innerHTML, options);
        }).first().parent();

        if (newActive.length > 0) {
            if (!lodash.isNil(curActive))
                curActive.removeClass('active');
            (curActive = newActive).addClass('active');
        }

        return !lodash.isNil(curActive) && curActive === newActive;
    }

    return {
        'inArray': inArray,
        'setActiveMenuItem': setActiveMenuitem
    }
})(_, $);