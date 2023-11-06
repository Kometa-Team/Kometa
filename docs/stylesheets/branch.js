// custom.js

// Function to check if the current URL contains "config" or "metadata"
function checkURLForBranch() {
  const currentURL = window.location.href;

  if (currentURL.indexOf("nightly") !== -1) {
    // If "config" is found in the URL, change the CSS of .md-header to red
    document.querySelector(".md-header").style.backgroundColor = "#ef5552";
    document.querySelector(".md-tabs").style.backgroundColor = "#ef5552";

    // Change the text of <span class="md-ellipsis">
    const ellipsisSpan = document.querySelector(".md-ellipsis");
    if (ellipsisSpan) {
      ellipsisSpan.textContent = "PMM Wiki - NIGHTLY BRANCH";
    }
  } else if (currentURL.indexOf("develop") !== -1) {
    // If "metadata" is found in the URL, change the CSS of .md-header to yellow
    document.querySelector(".md-header").style.backgroundColor = "#ffa724";
    document.querySelector(".md-tabs").style.backgroundColor = "#ffa724";

    // Change the text of <span class="md-ellipsis">
    const ellipsisSpan = document.querySelector(".md-ellipsis");
    if (ellipsisSpan) {
      ellipsisSpan.textContent = "PMM Wiki - DEVELOP BRANCH";
    }
  }
}

// Call the function on page load
window.addEventListener("load", checkURLForBranch);
