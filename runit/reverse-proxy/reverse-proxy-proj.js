// Info dialog
function _showInfoDialog() {
    _unbindShowInfoDialog();

    let htmlCode = '\
        <div style="font-weight: bold; font-size: 120%; padding-bottom: 10px;">General information about the Overleaf testing phase</div>\
        <div style="font-weight: normal; padding-bottom: 5px;">\
            <p>This version of <em>Overleaf</em> is currently in a <strong>testing phase</strong>.\
            This means that not all features might work as expected. If you run into any problems, feel free to contact us!</p>\
            <p><strong>Please note the following limitations when sharing projects:</strong>\
                <ul>\
                    <li>Sharing only works amongst <em>sciebo</em> users</li>\
                    <li>Target users of sharing must have used Overleaf <strong>at least once</strong></li>\
                </ul>\
            </p>\
            <p>Also note that your project files will <strong>not</strong> appear in your <em>sciebo</em> files.\
            If you want to save your project files to <em>sciebo</em>, export the project as a <strong>.zip</strong> file and upload it to manually.\
        </div>\
        <div style="text-align: right;"><button type="button" class="dlg-btn" data-msgpopup-close>Close</button></div>\
    ';

    $().msgpopup({
		text: htmlCode,
		time: false,
		x: false,
		closeFunc: () => { _bindShowInfoDialog(); },
	});
}

function _bindShowInfoDialog() {
    $('#support-info').unbind('click');
    $('#support-info').click((event) => {
        event.preventDefault();
        _showInfoDialog();
    });
}

function _unbindShowInfoDialog() {
    $('#support-info').unbind('click');
    $('#support-info').click((event) => {
        event.preventDefault();
    });
}

// Main hook
$(window).on("load", function() {
    _bindShowInfoDialog();
});
