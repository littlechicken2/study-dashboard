(() => {
  let lastPayload = "";
  let lastActivity = 0;

  function classify() {
    const host = location.hostname;
    const path = location.pathname;
    if (/bilibili\.com|youtube\.com|douyin\.com/.test(host)) return { category: "distraction", source: host };
    if (/tcfca\.cn/.test(host) && path.startsWith("/reading/")) return { category: "reading", source: "tcf-reading" };
    if (/chatgpt\.com|chat\.openai\.com/.test(host)) return { category: "contextual", source: "chatgpt" };
    if (host === "127.0.0.1" || host === "10.0.0.19") {
      if (/pdf_reader|a1_player/.test(path)) return { category: "grammar", source: "local-french" };
    }
    return null;
  }

  function showWarning() {
    if (document.getElementById("study-focus-warning")) return;
    const box = document.createElement("div");
    box.id = "study-focus-warning";
    box.textContent = "学习计时已暂停：关闭娱乐页面即可继续计时。";
    Object.assign(box.style, {
      position: "fixed",
      zIndex: "2147483647",
      top: "18px",
      left: "50%",
      transform: "translateX(-50%)",
      padding: "14px 18px",
      background: "#f25022",
      color: "#fff",
      fontSize: "18px",
      fontWeight: "700",
      borderRadius: "8px",
      boxShadow: "0 12px 40px rgba(0,0,0,.35)"
    });
    document.documentElement.appendChild(box);
  }

  function sendActivity(force = false) {
    if (document.hidden || !document.hasFocus()) return;
    const now = Date.now();
    if (!force && now - lastActivity < 10000) return;
    const info = classify();
    if (!info) return;
    lastActivity = now;
    if (info.category === "distraction") showWarning();
    fetch("http://127.0.0.1:8765/api/activity-ping", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...info,
        seconds: info.category === "distraction" ? 0 : 10,
        title: document.title,
        url: location.href,
        capturedAt: new Date().toISOString()
      })
    }).catch(() => {});
  }

  function visibleText() {
    return document.body?.innerText || "";
  }

  function readProgress() {
    const text = visibleText();
    const test = location.pathname.match(/\/reading\/(test\d+)/i)?.[1] || "unknown";
    const answered = text.match(/已答\s*(\d+)\s*\/\s*39/);
    const score = text.match(/分数\s*[:：]\s*(\d+)/);
    const timer = text.match(/计时\s*[:：]\s*(\d+):(\d+)/);
    if (!answered) return null;
    return {
      source: "tcfca.cn",
      test,
      answered: Number(answered[1]),
      total: 39,
      correct: score ? Number(score[1]) : 0,
      seconds: timer ? Number(timer[1]) * 60 + Number(timer[2]) : 0,
      capturedAt: new Date().toISOString()
    };
  }

  function sync() {
    const payload = readProgress();
    if (!payload) return;
    const serialized = JSON.stringify(payload);
    if (serialized === lastPayload) return;
    lastPayload = serialized;
    fetch("http://127.0.0.1:8765/api/reading-progress", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: serialized
    }).catch(() => {});
  }

  sync();
  sendActivity(true);
  setInterval(sync, 10000);
  setInterval(sendActivity, 10000);
  document.addEventListener("click", () => setTimeout(sync, 800), true);
  document.addEventListener("click", () => setTimeout(() => sendActivity(true), 800), true);
  window.addEventListener("focus", () => { sync(); sendActivity(true); });
})();
