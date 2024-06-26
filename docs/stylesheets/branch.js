function checkURLForBranch() {
  const currentURL = window.location.href;
  const ellipsisSpan = document.querySelector(".md-ellipsis");
  const mdBanner = document.querySelector(".md-banner"); // Select the banner element

  // Default text
  let ellipsisText = "Kometa Wiki";
  let bannerColor = "#252525"; // Default banner color

  if (currentURL.includes("en/nightly") || currentURL.includes("en/develop") {
    ellipsisText = currentURL.includes("en/nightly") ? "Kometa Nightly Wiki" : "Kometa Develop Wiki";
    bannerColor = "#611423"; // Updated banner color
  }

  // Create ellipsisSpan if it doesn't exist
  if (!ellipsisSpan) {
    ellipsisSpan = document.createElement("span");
    ellipsisSpan.classList.add("md-ellipsis");
    document.body.appendChild(ellipsisSpan);
  }

  ellipsisSpan.textContent = ellipsisText;

  // Update banner color
  if (mdBanner) {
    mdBanner.style.backgroundColor = bannerColor;
  }
}

window.addEventListener("load", checkURLForBranch);
