// Main hook
$(window).on("load", function() {
    // Inform the containing parent window about the login page being displayed
    window.parent.postMessage("login-page-displayed", "*");
});
