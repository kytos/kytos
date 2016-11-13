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

        var aEvenElements = [];
        var aOddElements = [];

        $.each(carouselItems, function (index, item) {
            if ( index % thisScope.owl.options.owlNrowNumberOfRows === 0 ) {
                aEvenElements.push(item);
            } else {
                aOddElements.push(item);
            }
        });

        carousel.empty();

        switch (thisScope.owl.options.owlNrowDirection) {
            case 'ltr':
                thisScope.leftToright(thisScope, carousel, carouselItems);
                break;

            default :
                thisScope.upTodown(thisScope, aEvenElements, aOddElements, carousel);
        }

    };

    OwlNrow.prototype.leftToright = function(thisScope, carousel, carouselItems){

        var owlContainerClass = thisScope.owl.options.owlNrowContainer;
        var owlMargin = thisScope.owl.options.margin;

        var carouselItemsLength = carouselItems.length;

        var rowsArrays = {};
        //var firsArr = [];
        //var secondArr = [];

        //console.log(carouselItemsLength);

        if (carouselItemsLength % thisScope.owl.options.owlNrowNumberOfRows === 0) {
            carouselItemsLength = carouselItemsLength/thisScope.owl.options.owlNrowNumberOfRows;
        } else {
            carouselItemsLength = ((carouselItemsLength - 1)/thisScope.owl.options.owlNrowNumberOfRows) + 1;
        }

        // split items into N arrays, one for each row.
        var current_row = 0;
        rowArrays[current_row] = [];
        $.each(carouselItems, function (index, item) {
          if (index % carouselItemsLength === 0) {
            current_array ++;
            rowArrays[current_row] = [];
          }
          rowsArray[current_row].push(item);
        });

        for (var i=0; i<rowsArray[0].length; i++) {
          var rowContainer = $('<div class="' + owlContainerClass + '"/>');

          $.each(rowArrays, function(index, row){
            var item = row[i];
                item.style.marginBottom = owlMargin + 'px';
            rowContainer.append(item);
          });

          carousel.append(rowContainer);
        }
    };

    OwlNrow.prototype.upTodown = function(thisScope, aEvenElements, aOddElements, carousel){

        var owlContainerClass = thisScope.owl.options.owlNrowContainer;
        var owlMargin = thisScope.owl.options.margin;

        $.each(aEvenElements, function (index, item) {

            var rowContainer = $('<div class="' + owlContainerClass + '"/>');
            var evenElement = aEvenElements[index];

            evenElement.style.marginBottom = owlMargin + 'px';

            rowContainer
                .append(evenElement)
                .append(aOddElements[index]);

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
