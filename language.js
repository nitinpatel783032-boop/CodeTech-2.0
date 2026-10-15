// ===== Code Master: Site-wide Language Switcher =====
(function () {
  var STORAGE_KEY = "cm_ai_language";

  // "value" app.py ke LANGUAGES dictionary ki keys se match hona chahiye
  var LANGS = [
    { value: "en", label: "English" },
    { value: "hi", label: "हिन्दी (Hindi)" },
    { value: "gu", label: "ગુજરાતી (Gujarati)" },
    { value: "mr", label: "मराठी (Marathi)" },
    { value: "bn", label: "বাংলা (Bengali)" },
    { value: "ta", label: "தமிழ் (Tamil)" },
    { value: "te", label: "తెలుగు (Telugu)" }
  ];

  function getLang() {
    return localStorage.getItem(STORAGE_KEY) || "en";
  }

  // ---- Part 1: Code Master AI ko selected language bhejna ----
  var originalFetch = window.fetch;
  window.fetch = function (url, options) {
    try {
      var u = typeof url === "string" ? url : url.url;
      if (u && u.indexOf("/api/chat") !== -1 && options && typeof options.body === "string") {
        var body = JSON.parse(options.body);
        body.language = getLang();
        options = Object.assign({}, options, { body: JSON.stringify(body) });
      }
    } catch (e) {}
    return originalFetch.call(this, url, options);
  };

  // ---- Part 2: Poori website ka translation (Google Translate) ----
  function setCookie(lang) {
    if (lang === "en") {
      var host = location.hostname;
      ["", "domain=" + host + ";", "domain=." + host + ";"].forEach(function (d) {
        document.cookie = "googtrans=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;" + d;
      });
    } else {
      document.cookie = "googtrans=/en/" + lang + ";path=/";
    }
  }

  function applyLanguage(lang) {
    localStorage.setItem(STORAGE_KEY, lang);
    setCookie(lang);
    if (lang === "en") {
      location.reload();
      return;
    }
    var combo = document.querySelector(".goog-te-combo");
    if (combo) {
      combo.value = lang;
      combo.dispatchEvent(new Event("change"));
    } else {
      location.reload();
    }
  }

  // Code blocks translate na ho, isliye notranslate laga do
  function markNoTranslate() {
    document.querySelectorAll("pre, code, textarea").forEach(function (el) {
      el.classList.add("notranslate");
      el.setAttribute("translate", "no");
    });
  }

  function init() {
    // CSS: Google ka banner chhupao + dropdown ka design
    var style = document.createElement("style");
    style.textContent =
      ".goog-te-banner-frame,.skiptranslate iframe{display:none!important}" +
      "body{top:0!important}" +
      "#cm-lang-box{position:fixed;left:20px;bottom:20px;z-index:9999;display:flex;align-items:center;" +
      "gap:6px;background:#1f2937;color:#fff;padding:8px 12px;border-radius:999px;" +
      "box-shadow:0 4px 14px rgba(0,0,0,.35);font-size:14px}" +
      "#cm-lang-box select{background:transparent;color:#fff;border:none;font-size:14px;" +
      "outline:none;cursor:pointer}" +
      "#cm-lang-box option{color:#000}";
    document.head.appendChild(style);

    // Google Translate ka hidden element
    var holder = document.createElement("div");
    holder.id = "google_translate_element";
    holder.style.display = "none";
    document.body.appendChild(holder);

    window.googleTranslateElementInit = function () {
      new google.translate.TranslateElement({
        pageLanguage: "en",
        includedLanguages: LANGS.map(function (l) { return l.value; }).join(","),
        autoDisplay: false
      }, "google_translate_element");
    };
    var s = document.createElement("script");
    s.src = "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    document.body.appendChild(s);

    // Hamara apna language dropdown
    var box = document.createElement("div");
    box.id = "cm-lang-box";
    box.innerHTML = '<span>🌐</span><select id="cm-lang-select"></select>';
    document.body.appendChild(box);

    var select = box.querySelector("#cm-lang-select");
    LANGS.forEach(function (l) {
      var opt = document.createElement("option");
      opt.value = l.value;
      opt.textContent = l.label;
      select.appendChild(opt);
    });
    select.value = getLang();
    select.addEventListener("change", function () {
      applyLanguage(select.value);
    });

    markNoTranslate();
    var t;
    new MutationObserver(function () {
      clearTimeout(t);
      t = setTimeout(markNoTranslate, 300);
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();