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

// Quote button: prefill the reply textarea with a [quote] block and jump to it.
document.addEventListener("click", (e) => {
  const b = e.target.closest(".quote-btn");
  if (!b) return;
  const ta = document.getElementById("id_body");
  if (!ta) return;
  ta.value += (ta.value ? "\n" : "") + `[quote=${b.dataset.author}]${b.dataset.body}[/quote]\n`;
  ta.focus();
  ta.scrollIntoView({ behavior: "smooth", block: "center" });
});

// ── Shoutbox: poll the feed, submit via fetch. Uses textContent (no innerHTML) ──
(function () {
  const box = document.getElementById("shoutbox");
  if (!box) return;
  const list = document.getElementById("shout-list");
  const form = document.getElementById("shout-form");
  const atBottom = () => list.scrollHeight - list.scrollTop - list.clientHeight < 40;

  function render(shouts) {
    const stick = atBottom();
    list.textContent = "";
    if (!shouts.length) {
      const p = document.createElement("p");
      p.className = "muted shout-empty";
      p.textContent = "No shouts yet — be the first.";
      list.appendChild(p);
    }
    for (const s of shouts) {
      const row = document.createElement("div");
      row.className = "shout";
      const u = document.createElement("a");
      u.className = "username " + s.cls;
      u.textContent = s.user;
      const b = document.createElement("span");
      b.className = "shout-body";
      b.textContent = s.body;
      const t = document.createElement("span");
      t.className = "shout-ago";
      t.textContent = s.ago;
      row.append(u, b, t);
      list.appendChild(row);
    }
    if (stick) list.scrollTop = list.scrollHeight;
  }

  async function poll() {
    try {
      const res = await fetch(box.dataset.feed, { headers: { "X-Requested-With": "fetch" } });
      if (res.ok) render((await res.json()).shouts);
    } catch (_) {}
  }

  if (form) {
    const input = form.querySelector("input[name=body]");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = input.value.trim();
      if (!body) return;
      input.disabled = true;
      try {
        const res = await fetch(box.dataset.post, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken"), "X-Requested-With": "fetch" },
          body: new URLSearchParams({ body }),
        });
        const d = await res.json();
        if (res.ok) {
          input.value = "";
          render(d.shouts);
          list.scrollTop = list.scrollHeight;
        } else if (d.error) {
          input.placeholder = d.error;
        }
      } catch (_) {} finally {
        input.disabled = false;
        input.focus();
      }
    });
  }

  list.scrollTop = list.scrollHeight;
  setInterval(poll, 7000);
})();
