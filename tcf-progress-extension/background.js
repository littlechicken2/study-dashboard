const LOOKUP_TAB_PATTERNS = [
  "https://www.freetcf.com/question*",
  "https://app.freetcf.com/question*",
  "https://www.frdic.com/dicts/fr/*"
];

chrome.tabs.query({ url: LOOKUP_TAB_PATTERNS }, tabs => {
  tabs.forEach(tab => {
    if (tab.id) chrome.tabs.reload(tab.id);
  });
});
