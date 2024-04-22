// custom.js

// Function to check if the current URL contains "nightly" or "develop" and adjust styles accordingly
function checkURLForBranch() {
  const currentURL = window.location.href;

  // Helper function to update style and text
  function updateTheme(headerColor, tabsColor, textContent) {
    const header = document.querySelector(".md-header");
    const tabs = document.querySelector(".md-tabs");
    const ellipsisSpan = document.querySelector(".md-ellipsis");

    if (header && tabs) { // Check if elements exist
      header.style.backgroundColor = headerColor;
      tabs.style.backgroundColor = tabsColor;
    }

    if (ellipsisSpan) { // Check if element exists
      ellipsisSpan.textContent = textContent;
    }
  }

  // Change theme based on URL segment
  if (currentURL.includes("en/nightly")) {
    updateTheme("#262dbd", "#262dbd", "Kometa Nightly Wiki");
  } else if (currentURL.includes("en/develop")) {
    updateTheme("#ffa724", "#ffa724", "Kometa Develop Wiki");
  }
}

// Call the function on page load
window.addEventListener("load", checkURLForBranch);