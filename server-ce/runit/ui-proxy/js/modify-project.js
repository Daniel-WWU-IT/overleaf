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

function addVersionToFooter() {
  const footerElem = $("footer");
  if (footerElem.length > 0) {
    const rowElem = footerElem.find("div[class='row']");
    if (rowElem.length > 0) {
      const footerItems = rowElem.find("ul");
      if (footerItems.length > 0) {
        const rightEntryElem = footerItems.last();

        if (rightEntryElem.find("li:contains(version)").length === 0) {
          rightEntryElem.find("li")?.html(`<strong>Overleaf version:</strong> ${OVERLEAF_VERSION} <strong>Integration version:</strong> ${INTEGRATION_VERSION}`);
          rightEntryElem.css("font-style", "italic");
        }
      }
    }
  }
}

// Entry hook
$(window).on("load", function() {
  addMutationsObserver(document.body, () => {
    adjustNavigationItems();
    addVersionToFooter();
  });
});
