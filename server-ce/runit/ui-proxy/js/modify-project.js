// Info dialog
function _showInfoDialog() {
  _unbindShowInfoDialog();

  let htmlCode = '\
        <div style="font-weight: bold; font-size: 120%; padding-bottom: 10px;">General information about the Overleaf integration</div>\
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
        <div style="display: grid; grid-template-columns: max-content auto min-content; align-items: center;">\
            <span style="font-size: 85%; font-weight: normal;"><strong>Overleaf version:</strong> ${OVERLEAF_VERSION} | <strong>Integration version:</strong> ${INTEGRATION_VERSION}</span>\
            <span>&nbsp;</span>\
            <button type="button" class="dlg-btn" data-msgpopup-close>Close</button>\
        </div>\
    ';

  htmlCode = htmlCode.replace("${OVERLEAF_VERSION}", OVERLEAF_VERSION);
  htmlCode = htmlCode.replace("${INTEGRATION_VERSION}", INTEGRATION_VERSION);

  $().msgpopup({
    text: htmlCode,
    time: false,
    x: false,
    closeFunc: () => { _bindShowInfoDialog(); },
  });
}

function _bindShowInfoDialog() {
  $("#nav-item-support-lnk").unbind("click");
  $("#nav-item-support-lnk").click((event) => {
    event.preventDefault();
    _showInfoDialog();
  });
}

function _unbindShowInfoDialog() {
  $("#nav-item-support-lnk").unbind('click');
  $("#nav-item-support-lnk").click((event) => {
    event.preventDefault();
  });
}


// Main modifiers
function addHeaderItems() {
  const navBar = $("ul[role='menubar']");
  if (navBar.length > 0) {
    if (navBar.find("#nav-item-support").length === 0) {
      navBar.append(`
        <li role="none" class="nav-item subdued" id="nav-item-support">
            <a id="nav-item-support-lnk" role="menuitem" href="#" class="nav-link" rel="noopener noreferrer">Help</a>
        </li>
    `);
    }

    if (navBar.find("#nav-item-contact").length === 0) {
      navBar.append(`
        <li role="none" class="nav-item" id="nav-item-contact">
            <a role="menuitem" href="https://hochschulcloud.nrw/de/kontakt" class="nav-link" target="_blank" rel="noopener noreferrer">Contact us</a>
        </li>
    `);
    }
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
    addHeaderItems();
    adjustNavigationItems();
    addVersionToFooter();

    _bindShowInfoDialog();
  });
});
