// Info dialog
function showInfoDialog() {
  const htmlCode = `
    <div id="info-dialog">
      <div style="font-weight: bold; font-size: 120%; padding-top: 5px; padding-bottom: 5px; margin-bottom: 10px; border-radius: 2px; text-align: center; background-color: rgb(9, 136, 66); color: white;">General Information and Help</div>
      <div style="font-weight: normal; padding-bottom: 5px; text-align: left;">
          <p style="font-size: 110%;">Welcome to <em>Overleaf</em> in <a href="https://www.sciebo.de" target="_blank">sciebo</a>!</p>
          <p>If you run into any problems, feel free to contact us! Simply use the button on the main page to open our contact form.</p>
          <p><strong>Please note the following limitations when sharing projects:</strong>
              <ul>
                  <li>Sharing only works amongst <em>sciebo</em> users</li>
                  <li>Target users of sharing must have used Overleaf <strong>at least once</strong></li>
              </ul>
          </p>
          <p>Also note that your project files will <strong>not</strong> appear in your <em>sciebo</em> files.
          If you want to save your project files to <em>sciebo</em>, export the project as a <strong>.zip</strong> file and upload it manually.
      </div>
      <div style="display: grid; grid-template-columns: max-content auto min-content; align-items: center;">
          <span style="font-size: 85%; font-weight: normal;"><strong>Overleaf version:</strong> ${OVERLEAF_VERSION} | <strong>Integration version:</strong> ${INTEGRATION_VERSION}</span>
          <span>&nbsp;</span>
          <button type="button" class="dlg-btn" data-msgpopup-close>Close</button>
      </div>
    </div>
  `;

  if ($.find("#info-dialog").length === 0) {
    $().msgpopup({
      text: htmlCode,
      time: false,
      x: false
    });
  }
}

// Main modifiers
function addHeaderItems() {
  const navBar = $("ul[role='menubar']");
  if (navBar.length > 0) {
    const navItemProjects = navBar.find("li[class='nav-item-projects nav-item']");
    if (navItemProjects.length > 0) {
      navItemProjects.hide();
    }

    if (navBar.find("#nav-item-support").length === 0) {
      navBar.append(`
        <li role="none" class="nav-item subdued" id="nav-item-support">
            <a role="menuitem" href="#" class="nav-link" rel="noopener noreferrer" onclick="showInfoDialog()">Help</a>
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
  // Hide some account controls
  const accName = $("div[class='ds-nav-ds-name']");
  if (accName.length > 0) {
    accName.hide();
  }
  const accSettings = $("li:has(a[href='/user/settings'])");
  if (accSettings.length > 0) {
    accSettings.hide();
  }
  const accLogout = $("li:has(form[id='logOutForm'])");
  if (accLogout.length > 0) {
    accLogout.prev()?.attr("style", "display: none !important;");
    accLogout.hide();
  }

  // Add text to account icon
  const accIcon = $("div[class='ds-nav-icon-dropdown dropdown']");
  if (accIcon.length > 0) {
    accIcon.attr("style", "align-items: center;");

    if (accIcon.find("#account-icon-text").length === 0) {
      accIcon.append(`<span id="account-icon-text" style="margin-left: 5px;">Account</span>`);
    }
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
  });
});
