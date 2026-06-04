(() => {
  let lastPayload = "";

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
  setInterval(sync, 10000);
  document.addEventListener("click", () => setTimeout(sync, 800), true);
  window.addEventListener("focus", sync);
})();
