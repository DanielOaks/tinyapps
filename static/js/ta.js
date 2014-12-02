/* TinyApps JS
** Written by Daniel Oaks
** Licensed under the BSD 2-clause license
*/

$(document).ready(function() {
    // add our own extension, .class_list() on an element returns the equiv. of .classList(), has _ to not collide
    $.fn.class_list = function() {return this.attr('class').split(/\s+/);};

    $('#header').on('click', '.proj', function() {
        $('.proj-select').toggleClass('shown');
    });

    // https://stackoverflow.com/questions/6635659/jquery-bind-click-anything-but-element
    // close project menu when clicked outside
    $(document).click(function(event) {
        if ((!$(event.target).is('.project-bar')) && ($(event.target).parents().index($('.project-bar')) == -1)) {
            if ($('.proj-select').hasClass('shown')) {
                $('.proj-select').removeClass('shown');
            }
        }
    })
});
