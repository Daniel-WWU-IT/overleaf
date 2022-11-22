;(function($) {

	$.fn.msgpopup = function( options ){
	    var msgClone;

		var opt = $.extend({
			text: '',
			type: 'normal',
			time: 5000,
			class: '',
			x: true,
			removeContainerOnClose: true,
			containerCheckItemBeforeRemove: true,
			success: null,
			id: false,
			scrollToBottomOnNewMessage: false,
			custom: false,

			closeFunc: true,
			mouseoverFunc: false,
			mouseoutFunc: false,
			beforeShowFunc: false,
			afterShowFunc: false,
			clickFunc: false,
			beforeRemoveFunc: false,
			afterRemoveFunc: false,

			themeClass: 'msgpopup-theme-default',
			defaultTypeClass: 'msgpopup-type',
			wrapVisibleClass: 'msgpopup-wrap-visible',
			appendTo: 'body',

			elToCloneData: 'data-msgpopup-to-clone',
			containerData: 'data-msgpopup-container',
			containerClass: 'msgpopup-container',
			boxContentData: 'data-msgpopup-content',
			boxContentClass: 'msgpopup-content',
			boxTextData: 'data-msgpopup-text',
			boxTextClass: 'msgpopup-text',
			boxCloneOutputData: 'data-msgpopup-box-clone-output',
			boxCloneOutputClass: 'msgpopup-box-clone-output',
			wrapData: 'data-msgpopup-wrap',
			wrapClass: 'msgpopup-wrap',
			itemData: 'data-msgpopup-item',
			itemClass: 'msgpopup-item',
			boxData: 'data-msgpopup-box',
			boxClass: 'msgpopup-box',
		}, options);

		/**
		 * Check func exists before exec
		 * ----------------------------------------------------------------------------------
		 */
		var execFunc = function(func, param){
		    if (func) {
		        func(param);
		    }
		}

		/**
		 * Init function
		 * ----------------------------------------------------------------------------------
		 */
		var init = function() {
			var checkIfMessagePopupHasInit = $('['+opt.containerData+']');
			if(checkIfMessagePopupHasInit.length <= 0) {
				$(opt.appendTo).append('\
				<div '+opt.containerData+' class="msgpopup '+opt.containerClass+' '+opt.themeClass+'">\
					<div '+opt.boxCloneOutputData+' class="'+opt.boxCloneOutputClass+'"></div>\
					<div '+opt.elToCloneData+' '+opt.boxData+' class="'+opt.boxClass+'">\
						<div '+opt.wrapData+' class="'+opt.wrapClass+'">\
							<div '+opt.itemData+' class="'+opt.itemClass+'">\
								<div '+opt.boxContentData+' class="'+opt.boxContentClass+'">\
									<div '+opt.boxTextData+' class="'+opt.boxTextClass+'"></div>\
								</div>\
							</div>\
						</div>\
					</div>\
				</div>');
			}

			if(opt.beforeShowFunc) {
				execFunc(opt.beforeShowFunc, {
					opt: opt,
					item: null,
					event: e
				});
			}

			show();

			return this;
		}

		/**
		 * Show function
		 * ----------------------------------------------------------------------------------
		 */
		var show = function(){

			// Clone default
			var container = $('['+opt.containerData+']');
			msgClone = $.extend(true, {}, container.find('['+opt.elToCloneData+']').clone());

			// Message type
			if(opt.success === true) {
				msgType = 'success';
			} else if(opt.success === false) {
				msgType = 'error';
			} else {
				var msgType = opt.type;
			}

			// Popup Mouse Hover Func
			if(opt.mouseoverFunc) {
				$(document).on({
					mouseenter: function(e) {
						execFunc(opt.mouseoverFunc, {
							opt: opt,
							item: msgClone,
							event: e
						});
					}
				}, msgClone);
			}

			// Popup Mouse Leave Func
			if(opt.mouseoutFunc) {
				$(document).on({
					mouseleave: function(e) {
						execFunc(opt.mouseoutFunc, {
							opt: opt,
							item: msgClone,
							event: e
						});
					}
				}, msgClone);
			}

			// Popup click Func
			if(opt.clickFunc) {
				$(document).on({
					click: function(e) {
						execFunc(opt.clickFunc, {
							opt: opt,
							item: msgClone,
							event: e
						});
					}
				}, msgClone);
			}

			// Add close button
			if(opt.x === true) {
				msgClone.find('['+opt.wrapData+']').append('<span class="msgpopup-close-container"><span data-msgpopup-close class="msgpopup-close-x"></span></span>');
			}

			// Insert text
			msgClone
			.find('['+opt.boxTextData+']')
			.html(opt.text);

			// Custom doesn't have default class
			if(opt.custom) {
				msgClone
				.find('['+opt.itemData+']')
				.removeClass(opt.itemClass)
				.removeClass(opt.defaultTypeClass)
				.find('['+opt.boxContentData+']')
				.removeClass(opt.boxContentClass)
			} else {
				msgClone
				.find('['+opt.itemData+']')
				.addClass((opt.defaultTypeClass === false ? '' : opt.defaultTypeClass)+' msgpopup-'+msgType+' '+msgType);
			}

			// Config to cloned
			msgClone
			.removeAttr(opt.elToCloneData)
			.attr('data-msgpopup-id', (opt.id ? opt.id : ''))
			.appendTo('['+opt.boxCloneOutputData+']')
			.slideDown(0)
			.removeClass('msgpopup-clone')
			.find('['+opt.itemData+']')
			.addClass(opt.class);

			// Finally, show :)
			msgClone
			.find('['+opt.wrapData+']')
			.addClass(opt.wrapVisibleClass);

			// Scroll to bottom if overflow
			if(opt.scrollToBottomOnNewMessage) {
				var container = $('['+opt.boxCloneOutputData+']');
				container.stop().animate({
					scrollTop: container.prop('scrollHeight')
				}, null);
			}

			// Close func
			if(opt.closeFunc) {
				msgClone.find('[data-msgpopup-close]').click(function(){
					//if(opt.closeFunc === true) {
						var item = $(this).parents('['+opt.boxData+']').eq(0);
						remove(item);
					//} else {
						execFunc(opt.closeFunc, {
							opt: opt,
							item: msgClone,
						});
					//}
				});
			}

			// Time to remove
			if(typeof(opt.time) === 'number') {
				setTimeout(function(){
					remove(msgClone);
				}, opt.time);
			}

			// After show func
			if(opt.afterShowFunc) {
				execFunc(opt.afterShowFunc, {
					opt: opt,
					item: msgClone,
					event: e
				});
			}

			return this;
		}

		/**
		 * Remove clone function
		 * ----------------------------------------------------------------------------------
		 */
		var remove = function(item) {

			var container = item.parents('['+opt.containerData+']').eq(0);
			item.find('['+opt.wrapData+']').removeClass(opt.wrapVisibleClass);

			// Before remove func
			if(opt.beforeRemoveFunc) {
				$(document).on({
					click: function(e) {
						execFunc(opt.beforeRemoveFunc, {
							opt: opt,
							item: msgClone,
							event: e
						});
					}
				}, msgClone);
			}

			// Animate to remove
			/*item.animate({
				height: 0,
				padding: 0
			}, null, function(){*/
				item.remove();
				if(opt.removeContainerOnClose) {
					if(opt.containerCheckItemBeforeRemove) {
						if(container.find('['+opt.boxCloneOutputData+']').find('['+opt.boxData+']').length <= 0) {
							container.remove();
						}
					}
				}
				if(opt.afterRemoveFunc) {
					$(document).on({
						click: function(e) {
							execFunc(opt.afterRemoveFunc, {
								opt: opt,
								item: msgClone,
								event: e
							});
						}
					}, msgClone);
				}
				msgClone = null;
			/*});*/
		}

		init();

		return this;
	}

})(jQuery);
