// Main modifiers
function addSupportDropdown() {
  const navBar = $("ul[role='menubar']");
  if (navBar.length > 0 && navBar.find("#nav-item-support").length === 0) {
    /*
    <li role="none" class="nav-item-account dropdown" style="">
   <button type="button" id="react-aria2017518729-:r0:" aria-expanded="false" role="menuitem" class="dropdown-toggle btn btn-primary" aria-haspopup="true">
      Account
      <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 256 256" class="ms-2">
         <path d="M216.49,104.49l-80,80a12,12,0,0,1-17,0l-80-80a12,12,0,0,1,17-17L128,159l71.51-71.52a12,12,0,0,1,17,17Z"></path>
      </svg>
   </button>
   <ul role="menu" aria-labelledby="react-aria2017518729-:r0:" data-bs-popper="static" class="dropdown-menu dropdown-menu-end">
      <li role="menuitem" aria-disabled="true" data-rr-ui-dropdown-item="" class="dropdown-item disabled">admin@overleaf.nextcloud.dev.local</li>
      <li class="d-none d-lg-block dropdown-divider" role="separator"></li>
      <li role="none"><a href="/user/settings" role="menuitem" data-rr-ui-dropdown-item="" class="dropdown-item">Account settings</a></li>
      <li class="d-none d-lg-block dropdown-divider" role="separator"></li>
      <li role="none">
         <button type="submit" form="logOutForm" role="menuitem" data-rr-ui-dropdown-item="" class="d-flex align-items-center justify-content-between dropdown-item">
            <span>Log Out</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
               <path d="M120,216a8,8,0,0,1-8,8H48a8,8,0,0,1-8-8V40a8,8,0,0,1,8-8h64a8,8,0,0,1,0,16H56V208h56A8,8,0,0,1,120,216Zm109.66-93.66-40-40a8,8,0,0,0-11.32,11.32L204.69,120H112a8,8,0,0,0,0,16h92.69l-26.35,26.34a8,8,0,0,0,11.32,11.32l40-40A8,8,0,0,0,229.66,122.34Z"></path>
            </svg>
         </button>
         <form id="logOutForm" method="POST" action="/logout"><input type="hidden" name="_csrf" value="BvMRhwNn-ODQI-VYE-M8nFCpUY3sZ_6mDReE"></form>
      </li>
   </ul>
</li>
     */
    navBar.append(`
        <li role="none" class="nav-item dropdown" id="nav-item-support">
            <button type="button" id="nav-item-btn-support" role="menuitem" aria-expanded="false" aria-haspopup="true" class="dropdown-toggle btn btn-primary">
                Support<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" viewBox="0 0 256 256" class="ms-2"><path d="M216.49,104.49l-80,80a12,12,0,0,1-17,0l-80-80a12,12,0,0,1,17-17L128,159l71.51-71.52a12,12,0,0,1,17,17Z"></path></svg>
            </button>
            <ul role="menu" data-bs-popper="static" aria-labelledby="nav-item-btn-support" class="dropdown-menu dropdown-menu-end">
                <li role="menuitem" aria-disabled="true" data-rr-ui-dropdown-item="" class="dropdown-item disabled">admin@overleaf.nextcloud.dev.local</li>
            </ul>
        </li>
    `);
  }
}

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
        const leftEntryElem = footerItems.first();
        const rightEntryElem = footerItems.last();

        leftEntryElem.removeClass("col-lg-9");
        leftEntryElem.addClass("col-lg-6");
        rightEntryElem.removeClass("col-lg-9");
        rightEntryElem.addClass("col-lg-6");

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
    addSupportDropdown();
    adjustNavigationItems();
    addVersionToFooter();
  });
});
