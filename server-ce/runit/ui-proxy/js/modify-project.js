// Main modifiers
function adjustNavigationItems() {
  // Hide account controls
  const accGroup = $("div[class='ds-nav-sidebar-lower']");
  if (accGroup.length > 0) {
    accGroup.hide();
  }

  // Hide the main account button
  const accBtn = $("li[class='nav-item-account dropdown']");
  if (accBtn.length > 0) {
    accBtn.hide();
  }
}

// Entry hook
$(window).on("load", function() {
  addMutationsObserver(document.body, () => {
    adjustNavigationItems();
  });
});
