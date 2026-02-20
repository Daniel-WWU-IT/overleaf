// Main modifiers
function adjustFooterItems() {
  // Change footer link
  const footerLnk = $("a[href='https://www.overleaf.com/for/enterprises']");
  if (footerLnk.length > 0) {
    footerLnk.attr("href", "https://www.overleaf.com")
    footerLnk.attr("target", "_blank")
  }

  const navMainDiv = $("div[class='project-ds-nav-main']");
  if (navMainDiv.length > 0) {
    navMainDiv.css("min-height", "calc(100vh - 7.5rem)");
  }
}

// Entry hook
$(window).on("load", function() {
  addMutationsObserver(document.body, () => {
    adjustFooterItems();
  });
});
