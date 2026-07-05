// AJAX rep/like toggle. Degrades to a normal POST (server redirects) if this fails.
function getCookie(name) {
  const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return m ? decodeURIComponent(m.pop()) : "";
}

document.addEventListener("submit", async (e) => {
  const form = e.target.closest(".like-form");
  if (!form) return;
  e.preventDefault();
  const btn = form.querySelector(".like-btn");
  btn.disabled = true;
  try {
    const res = await fetch(form.action, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken"), "X-Requested-With": "fetch" },
    });
    if (res.ok) {
      const d = await res.json();
      form.querySelector(".like-count").textContent = d.count;
      btn.classList.toggle("liked", d.liked);
    }
  } catch (_) {
    form.submit(); // fall back to full-page POST
  } finally {
    btn.disabled = false;
  }
});
