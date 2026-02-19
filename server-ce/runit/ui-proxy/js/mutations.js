function addMutationsObserver(element, callback, initCall = true) {
  const observer = new MutationObserver((mutations, observer) => {
    for (const mutation of mutations) {
      if (mutation.type === "childList") {
        callback();
        break;
      }
    }
  });
  observer.observe(element, {childList: true, subtree: true});

  if (initCall) {
    callback();
  }
}
