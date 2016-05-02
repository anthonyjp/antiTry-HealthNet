/**
 * Created by Matthew on 2/27/2016.
 */

var registry = {};
registry = (function () {
    const NONE_CHOICE = '__NONE__';
    var curActive = null;

    function register(key) {
        if (has(key))
            return;

        var layers = _.toPath(key);
        var obj = registry;
        var i = 0;

        while (i++ < layers.length) {
            var next = layers[i - 1];

            if (!(next in obj))
                obj[next] = {};

            obj = obj[next]
        }

        return registry
    }

    function has(key) {
        var layers = _.toPath(key);
        var obj = registry;
        var i = 0;

        while (i++ < layers.length) {
            var next = layers[i-1];

            if(!(next in obj))
                return false;

            obj = obj[next];
        }

        return layers[i] in obj;
    }

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
        if (_.isNil(elem) || _.isNil(arr) || !_.isArrayLikeObject(arr))
            throw new TypeError('inArray expects non-nil element and non-nil array-like (iterable)!');

        return _.some(arr, function (x) {
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
        if (_.isNil(html_content) || !_.isString(html_content))
            return false;

        var options = _.trim(html_content).split('|');
        var nilActive = _.isNil(curActive);
        const IS_NONE = inArray(NONE_CHOICE, options);

        if(!IS_NONE) {
            var newActive = $('li.hn-menuitem > a').filter(function () {
                return inArray(this.innerHTML, options);
            }).first().parent();

            if (newActive.length > 0) {
                if (!nilActive)
                    curActive.removeClass('active');
                (curActive = newActive).addClass('active');
            }

            return !_.isNil(curActive) && curActive === newActive;
        } else {
            if(!nilActive)
                curActive.removeClass('active');

            curActive = null;
            return true;
        }
    }

    function initUserSearch() {
        var renderName = function (data, escape) {
            console.log('called');

            // Requires an image url, a url to the user profile, a user name, and a user type
            const html =
                "<div class=\"search-result\">" +
                "<div class=\"small-avatar-box\">" +
                "<img id=\"avatar\" class=\"center small-avatar\" src=\"%s\" />" +
                "</div>" +
                "<div class=\"small-content-box\">" +
                "<h5 id=\"search-result-name\"><a href=\"%s\">%s</a></h5>" +
                "<h6 id=\"search-result-name\">%s</h6>" +
                "</div>" +
                "</div>";

            return sprintf(html, escape(data.img), escape(data.profileUrl), escape(data.name), escape(data.type));
        };

        $.ajax({
            url: '/user',
            type: 'GET',
            data: {'list': true},
            cache: false,
            dataType: 'json',
            headers: {'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').val()},
            success: function (resp) {
                $('#user-search').selectize({
                    options: resp.users,
                    maxOptions: 100,
                    closeAfterSelect: true,
                    valueField: 'profileUrl',
                    labelField: 'name',
                    onChange: function (value) {
                        console.log(value);
                        window.location.href = value;
                    },
                    searchField: ['name'],
                    render: {option: renderName}
                });

                console.log('Search Utility Initialized');
            },
            failure: function (resp) {
                console.error('Failed to initialize search utility! Could not retrieve users...');
                console.dir(resp);
            }
        })
    }

    var entityMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': '&quot;',
        "'": '&#39;',
        "/": '&#x2F;'
    };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'\/]/g, function (s) {
            return entityMap[s];
        });
    }

    function getCsrf(tree) {
        return registry['utility']['getCsrf']();
    }

    function stopEventBehavior(event) {
        registry['utility']['stopEventBehavior'](event);
    }

    return {
        'NO_MENUITEM': NONE_CHOICE,
        'has': has,
        'module': register,
        'inArray': inArray,
        'setActiveMenuItem': setActiveMenuitem,
        'initUserSearch': initUserSearch,
        'escapeHtml': escapeHtml,
        'getCsrf': getCsrf,
        'stopEventBehavior': stopEventBehavior
    }
})();

registry.module('utility');
registry.module('forms');
registry.module('forms');
registry.module('auth');
registry.module('data');

Object.size = function (obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

Array.prototype.copy = function () {
    return this.slice(0);
};