var options =
{
        listItems : [],
        selectedTour: -1,
        effect: 'blink',
        objTable: '',
        icount: 0
};

var objTable;
var matchTable;

function initSelectList(id, listItems) {

    var self = $(id);

    /* Adding left box */
    var container = $('<div/>').addClass('selectList');
    var toolbar = $('<div/>').addClass('toolbar');
    toolbar.append($('<div/>').addClass('filterbox').text('Tournaments'));
    var tableDiv = $('<div/>').addClass('table_div');

    objTable = $('<table/>').addClass('table');

    tableDiv.append(objTable);
    container.append(toolbar);
    container.append(tableDiv);
    self.append(container);

    /* Adding right box */
    var container2 = $('<div/>').addClass('selectList');
    var toolbar2 = $('<div/>').addClass('toolbar');
    toolbar2.append($('<div/>').addClass('filterbox').text('Matches'));

    var tableDiv2 = $('<div/>').addClass('table_div');
    matchTable = $('<table/>').addClass('table');
    tableDiv2.append(matchTable);

    container2.append(toolbar2);
    container2.append(tableDiv2);
    self.append(container2);


    console.log(listItems);
    objTable.empty();
    jQuery.each(listItems, function () {


        var itemId = 'itm_t' + (options.icount++);	// generate item id
        var itm = $('<tr/>').css('height', '19px');
        var chk = $('<input/>').attr('type', 'checkbox').attr('id', itemId)
            .addClass('chk_tour')
            .attr('data-text', this.text)
            .attr('data-games', this.games)
            .attr('data-value', this.value).css('width', '0').css('display', 'none');

        itm.append($('<td/>').css('width', '0').append(chk));

        var label = $('<label/>').attr('for', itemId).text(this.text);
        itm.append($('<td/>').append(label));

        itm.off('click').on({click: function(){_selChange()}});
        objTable.append(itm);
    });
}

function _selChange() {
    var o = options;

    var prev_tour = o.selectedTour;

    // Scan elements and find checked ones.
    objTable.find('.chk_tour').each(function() {
        $(this).parent().removeClass('highlight').siblings().removeClass('highlight');
        if($(this).attr('checked')) {
            $(this).attr('checked', false);
            $(this).parent().removeClass('highlight').siblings().removeClass('highlight');
            if ($(this).attr('data-value') != prev_tour) {
                o.selectedTour = $(this).attr('data-value');
                $(this).parent().addClass('highlight').siblings().addClass('highlight');
                matchTable.empty();
                console.log($(this).attr('data-games'));

                var splited = $(this).attr('data-games').split(",");
                jQuery.each(splited, function () {
                    var itm = $('<tr/>').css('height', '19px');
                    var chk = $('<input/>').attr('type', 'checkbox').attr('id', "test")
                        .addClass('game_item')
                        .css('width', '0').css('display', 'none');

                    itm.append($('<td/>').css('width', '0').append(chk));

                    var label = $('<label/>').text(this);
                    itm.append($('<td/>').append(label));
                    matchTable.append(itm);
                });
            } else {
                o.selectedTour = -1;
                $(this).parent().removeClass('highlight').siblings().removeClass('highlight');
            }
        }
    });



    move_pointer(o.selectedTour);

}




