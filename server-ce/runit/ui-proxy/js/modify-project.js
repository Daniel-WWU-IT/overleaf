// Main modifiers
function adjustNavigationBar() {
  // Hide the lower portion of the navigation bar (account controls etc.)
  const accGroup = $("div[class='ds-nav-sidebar-lower']");
  if (accGroup.length > 0) {
    accGroup.hide();
  }
}

// Entry hook
$(window).on("load", function() {
  addMutationsObserver(document.body, () => {
    adjustNavigationBar();
  });
});
