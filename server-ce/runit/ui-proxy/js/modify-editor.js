// Main modifiers
function adjustMenuItems() {
  // Change the "Documentation" link
  const documentationMenuItem = $("div:contains('Documentation')");
  if (documentationMenuItem.length > 0) {
    const link = documentationMenuItem.closest("a");
    const parent = documentationMenuItem.closest("li");
    link?.attr("href", "https://www.overleaf.com/learn");
    link?.attr("target", "_blank");
    parent?.next("li")?.hide();
  }

  // Hide the "Contact us" item
  const contactMenuItem = $("div:contains('Contact us')");
  if (contactMenuItem.length > 0) {
    contactMenuItem.closest("li")?.hide();
  }
}

// Entry hook
$(window).on("load", function() {
  addMutationsObserver(document.body, () => {
    adjustMenuItems();
  });
});
