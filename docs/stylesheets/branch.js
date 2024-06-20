function checkURLForBranch() {
  const currentURL = window.location.href;

  // Select elements for background and text changes
  const headerAndTabs = document.querySelectorAll(".md-header, .md-tabs");
  const ellipsisSpan = document.querySelector(".md-ellipsis"); // Select ellipsisSpan

  if (headerAndTabs.length > 0) {
    let backgroundImage = "https://raw.githubusercontent.com/Kometa-Team/Kometa/nightly/docs/assets/background.jpg";
    let ellipsisText = ""; // Initialize ellipsisText

    if (currentURL.includes("en/nightly")) {
      backgroundImage = "https://raw.githubusercontent.com/Kometa-Team/Kometa/nightly/docs/assets/backgroundnightly.jpg";
      ellipsisText = "Kometa Nightly Wiki"; // Set text for Nightly
    } else if (currentURL.includes("en/develop")) {
      backgroundImage = "https://raw.githubusercontent.com/Kometa-Team/Kometa/nightly/docs/assets/backgrounddevelop.jpg";
      ellipsisText = "Kometa Develop Wiki"; // Set text for Develop
    }

    headerAndTabs.forEach(element => {
      element.style.backgroundImage = `url(${backgroundImage})`;
    });

    // Update ellipsisSpan text only if it exists
    if (ellipsisSpan) {
      ellipsisSpan.textContent = ellipsisText;
    }
  }
}

window.addEventListener("load", checkURLForBranch);
