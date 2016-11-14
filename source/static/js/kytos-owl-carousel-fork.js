/**
 * OwlNrow
 * @since 2.0.1
 * based on:
 *   - http://jsfiddle.net/joz63udn/6/
 *   - https://github.com/OwlFonk/OwlCarousel/issues/47
 */
;(function ($, window, document, undefined) {
    OwlNrow = function (scope) {
        this.owl = scope;
        this.owl.options = $.extend(OwlNrow.Defaults, this.owl.options);
        //link callback events with owl carousel here

        this.handlers = {
            'initialize.owl.carousel': $.proxy(function (e) {
                if (this.owl.settings.owlNrow) {
                    this.buildNrow(this);
                }
            }, this)
        };

        this.owl.$element.on(this.handlers);
    };

    OwlNrow.Defaults = {
        owlNrow: false,
        owlNrowTarget: 'item',
        owlNrowContainer: 'owlNrow-item',
        owlNrowNumberOfRows: 1,
        owlNrowDirection: 'utd', // ltr
    };

    //mehtods:
    OwlNrow.prototype.buildNrow = function(thisScope){

        var carousel = $(thisScope.owl.$element);
        var carouselItems = carousel.find('.' + thisScope.owl.options.owlNrowTarget);

        carousel.empty();

        switch (thisScope.owl.options.owlNrowDirection) {
            case 'ltr':
                thisScope.leftToright(thisScope, carousel, carouselItems);
                break;

            default :
                thisScope.upTodown(thisScope, carousel, carouselItems);
        }

    };

    OwlNrow.prototype.leftToright = function(thisScope, carousel, carouselItems){

        var owlContainerClass = thisScope.owl.options.owlNrowContainer;
        var owlMargin = thisScope.owl.options.margin;

        var carouselItemsLength = carouselItems.length;

        var rowsArrays = {},
            nrows = thisScope.owl.options.owlNrowNumberOfRows;

        rowLength = Math.ceil(carouselItems.length / nrows);

        // create the array for each row
        for (i=0; i < nrows; i++) {
          rowsArrays[i] = [];
        }

        $.each(carouselItems, function (index, item) {
          rowsArrays[Math.floor(index/rowLength)].push(item)
        });

        $.each(rowsArrays[0], function (index, item) {
            var rowContainer = $('<div class="' + owlContainerClass + '"/>');

            for (i=0; i < nrows; i++) {
              var element = rowsArrays[i][index];
              if (element) {
                element.style.marginBottom = owlMargin + 'px';
                rowContainer.append(element);
              }
            }

            carousel.append(rowContainer);
        });

    };

    OwlNrow.prototype.upTodown = function(thisScope, carousel, carouselItems){

        var rowsArrays = {};
        var nrows = thisScope.owl.options.owlNrowNumberOfRows;

        // create the array for each row
        for (i=0; i < nrows; i++) {
          rowsArrays[i] = [];
        }

        // split the items into the rows by up to down
        $.each(carouselItems, function (index, item) {
          rowsArrays[index % nrows].push(item)
        });

        var owlContainerClass = thisScope.owl.options.owlNrowContainer;
        var owlMargin = thisScope.owl.options.margin;

        // create the div elements and populate the carousel.
        $.each(rowsArrays[0], function (index, item) {

            var rowContainer = $('<div class="' + owlContainerClass + '"/>');

            for (i=0; i < nrows; i++) {
              var element = rowsArrays[i][index];
              if (element) {
                element.style.marginBottom = owlMargin + 'px';
                rowContainer.append(element);
              }
            }
            carousel.append(rowContainer);
        });
    };

    /**
     * Destroys the plugin.
     */
    OwlNrow.prototype.destroy = function() {
        var handler, property;

        for (handler in this.handlers) {
            this.owl.dom.$el.off(handler, this.handlers[handler]);
        }
        for (property in Object.getOwnPropertyNames(this)) {
            typeof this[property] !== 'function' && (this[property] = null);
        }
    };

    $.fn.owlCarousel.Constructor.Plugins['owlNrow'] = OwlNrow;
})( window.Zepto || window.jQuery, window,  document );
