// Handlers
function _handleFileTree() {
    let helpCont = $("div[class='documentation-btn-container']");
    if (helpCont.length > 0) {
        // Just hide this tree portion
        helpCont.hide();
    }
}

function _handleShareProjectDialog(dialog) {
    // Hide the 'link sharing' section
    dialog.find("div.public-access-level").hide();
    // Fix layout
    dialog.find("div.modal-body-share").css("padding-top", "10px");
}

function _handlePopupDialogs() {
    let dialog = $("div[role='dialog']");
    if (dialog.length > 0) {
        // Handle the 'Share Project' dialog
        if (dialog.find("h4:contains(Share Project)").length > 0) {
            _handleShareProjectDialog(dialog);
        }
    }
}

// Mutations helpers
function _addMutationsObserver(element, callback) {
    let observer = new MutationObserver(callback);
    observer.observe(element, {childList: true, subtree: true});
}

function _mutationsChildListHasChanged(mutations) {
    for (const mutation of mutations) {
        if (mutation.type === "childList") {
            return true;
        }
    }
    return false;
}

// Main hook
$(window).on("load", function() {
    // Listen to dynamic DOM changes
    const callback = (mutations, observer) => {
        if (_mutationsChildListHasChanged(mutations)) {
            _handleFileTree();
            _handlePopupDialogs();
        };
    }
    _addMutationsObserver(document.body, callback)
});
