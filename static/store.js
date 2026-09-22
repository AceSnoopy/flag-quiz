(() => {
  const search = document.getElementById("search");
  const region = document.getElementById("region");
  const hideOwned = document.getElementById("hide-owned");
  const cards = [...document.querySelectorAll("#grid .flag-card")];
  const empty = document.getElementById("empty");

  try {
    region.value = localStorage.getItem("store-region") || "";
    hideOwned.checked = localStorage.getItem("store-hide-owned") === "1";
  } catch {}

  function apply() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    for (const c of cards) {
      const visible =
        (!q || c.dataset.name.includes(q)) &&
        (!region.value || c.dataset.region === region.value) &&
        !(hideOwned.checked && c.classList.contains("owned"));
      c.hidden = !visible;
      if (visible) shown++;
    }
    empty.hidden = shown > 0;
    try {
      localStorage.setItem("store-region", region.value);
      localStorage.setItem("store-hide-owned", hideOwned.checked ? "1" : "0");
    } catch {}
  }

  search.addEventListener("input", apply);
  region.addEventListener("change", apply);
  hideOwned.addEventListener("change", apply);
  apply();
})();
