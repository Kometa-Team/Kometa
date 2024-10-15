document.addEventListener("DOMContentLoaded", () => {
  const currentURL = window.location.href;
  const ellipsisSpan = document.querySelector(".md-ellipsis");
  const mdBanner = document.querySelector(".md-banner");

  let ellipsisText = "Kometa Wiki";

  if (currentURL.includes("en/nightly") || currentURL.includes("en/develop")) {
    ellipsisText = currentURL.includes("en/nightly") ? "Kometa Nightly Wiki" : "Kometa Develop Wiki";
    bannerColor = "#611423";
  }

  if (!ellipsisSpan) {
    ellipsisSpan = document.createElement("span");
    ellipsisSpan.classList.add("md-ellipsis");
    document.body.appendChild(ellipsisSpan);
  }

  ellipsisSpan.textContent = ellipsisText;

  if (mdBanner) {
    mdBanner.style.setProperty('background-color', bannerColor, 'important');
  }
});
