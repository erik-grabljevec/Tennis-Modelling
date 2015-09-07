(function($) {
	$.widget("ui.checkList", {	
		options: {
			listItems : [],
			selectedItems: [],
			effect: 'blink',
			onChange: {},
			objTable: '',
			icount: 0
		},
		
		_create: function() {
			var self = this, o = self.options, el = self.element;

			// generate outer div
			var container = $('<div/>').addClass('checkList');

			// generate toolbar
			var toolbar = $('<div/>').addClass('toolbar');
			var chkAll = $('<input/>').attr('type','checkbox').addClass('chkAll').click(function(){
				var state = $(this).attr('checked');
				var setState = false;
				
				setState = (state==undefined) ? false : true;

				o.objTable.find('.chk:visible').attr('checked', setState);

				self._selChange();
			});
			// chkAll.on({click: function(){dragit.trajectory.removeAll()}});
			var txtfilter = $('<input/>').attr('type','text').addClass('txtFilter').keyup(function(){
				self._filter($(this).val());
			});
			toolbar.append($('<div/>').addClass('selectall').text('Select all: ').append(chkAll));
			toolbar.append($('<div/>').addClass('filterbox').text('Find player: ').append(txtfilter));

			// generate list table object
            var tableDiv = $('<div/>').addClass('table_div');
			o.objTable = $('<table/>').addClass('table');
            tableDiv.append(o.objTable);
			
			container.append(toolbar);
			container.append(tableDiv);
			el.append(container);

			self.loadList();
		},

		_addItem: function(listItem){
			var self = this, o = self.options, el = self.element;

			var itemId = 'itm' + (o.icount++);	// generate item id
			var itm = $('<tr/>');
			var chk = $('<input/>').attr('type','checkbox').attr('id',itemId)
					.addClass('chk')
					.attr('data-text',listItem.text)
					.attr('data-value',listItem.value);
			
			itm.append($('<td/>').append(chk));
			var label = $('<label/>').attr('for',itemId).text(listItem.text);
			itm.append($('<td/>').append(label));
			o.objTable.append(itm);

			// bind selection-change
			el.off('click').on({click: function(){self._selChange()}});
		},

		loadList: function(){
			var self = this, o = self.options, el = self.element;

			o.objTable.empty();
			$.each(o.listItems,function(){
				self._addItem(this);
			});
		},

		_selChange: function(){
			var self = this, o = self.options, el = self.element;

			// empty selection
			o.selectedItems = [];

			// scan elements, find checked ones
			o.objTable.find('.chk').each(function(){
				if($(this).attr('checked')){
					o.selectedItems.push({
						text: $(this).attr('data-text'),
						value: $(this).attr('data-value')
					});
					$(this).parent().addClass('highlight').siblings().addClass('highlight');
				}else{
					$(this).parent().removeClass('highlight').siblings().removeClass('highlight');
				}
			});

			// fire onChange event
			console.log(o.onChange);
			o.onChange.call();
		},

		_filter: function(filter){
			var self = this, o = self.options, el = self.element;

			o.objTable.find('.chk').each(function(){	
				if($(this).attr('data-text').toLowerCase().indexOf(filter.toLowerCase())>-1)
				{
					$(this).parent().parent().show(o.effect);
				}
				else{
					$(this).parent().parent().hide(o.effect);
				}
			});
		},

		getSelection: function(){
			var self = this, o = self.options, el = self.element;
			return o.selectedItems;
		},

		setData: function(dataModel){
			var self = this, o = self.options, el = self.element;
			o.listItems = dataModel;
			self.loadList();
			self._selChange();
		}
	});
})(jQuery); 