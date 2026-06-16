(() => {
  let lastPayload = "";
  let lastActivity = 0;
  let focusBlocker = null;

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

  async function dailyTasksComplete() {
    try {
      const data = await fetch("http://127.0.0.1:8765/data/progress.json?t=" + Date.now()).then(r => r.json());
      const reading = Boolean(data.reading?.today?.activityComplete || data.activity?.today?.readingMinutes > 0);
      const grammar = Boolean(data.course?.today?.activityComplete || data.activity?.today?.grammarMinutes > 0);
      const verb = Boolean(data.anki?.today?.activityComplete || data.activity?.today?.verbMinutes > 0);
      return reading && grammar && verb;
    } catch (_) {
      return false;
    }
  }

  function suppressMedia() {
    document.querySelectorAll("video, audio").forEach(media => {
      media.muted = true;
      media.volume = 0;
      media.pause?.();
      media.style.filter = "blur(18px) grayscale(1) brightness(.2)";
    });
  }

  function restoreMedia() {
    document.querySelectorAll("video, audio").forEach(media => {
      media.style.filter = "";
    });
  }

  function showWarning() {
    suppressMedia();
    if (focusBlocker) return;
    const box = document.createElement("div");
    focusBlocker = box;
    box.id = "study-focus-warning";
    box.innerHTML = `
      <div style="font-size:42px;font-weight:900;line-height:1.05;margin-bottom:18px">今天的学习任务还没完成</div>
      <div style="font-size:20px;line-height:1.55;max-width:760px;margin:0 auto 22px">
        Bilibili / YouTube / 抖音已暂停。先完成 Reading、Grammar、Verb 三项记录，再回来放松。
      </div>
      <div id="study-focus-status" style="font-size:16px;opacity:.9">正在检查监督台进度...</div>
    `;
    Object.assign(box.style, {
      position: "fixed",
      zIndex: "2147483647",
      inset: "0",
      display: "grid",
      placeItems: "center",
      textAlign: "center",
      padding: "34px",
      background: "rgba(7,18,15,.96)",
      color: "#fff",
      fontFamily: "Inter, system-ui, sans-serif",
      boxShadow: "inset 0 0 0 10px #f25022"
    });
    document.documentElement.appendChild(box);
  }

  function hideWarning() {
    focusBlocker?.remove();
    focusBlocker = null;
    restoreMedia();
  }

  async function enforceDistractionBlock() {
    const info = classify();
    if (!info || info.category !== "distraction") return;
    const complete = await dailyTasksComplete();
    if (complete) {
      hideWarning();
      return;
    }
    showWarning();
    const status = document.getElementById("study-focus-status");
    if (status) status.textContent = "未完成：娱乐视频已静音并暂停。关闭此页面，完成任务后会自动解锁。";
  }

  function sendActivity(force = false) {
    if (document.hidden || !document.hasFocus()) return;
    const now = Date.now();
    if (!force && now - lastActivity < 10000) return;
    const info = classify();
    if (!info) return;
    lastActivity = now;
    if (info.category === "distraction") enforceDistractionBlock();
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
  enforceDistractionBlock();
  setInterval(sync, 10000);
  setInterval(sendActivity, 10000);
  setInterval(enforceDistractionBlock, 3000);
  document.addEventListener("click", () => setTimeout(sync, 800), true);
  document.addEventListener("click", () => setTimeout(() => sendActivity(true), 800), true);
  window.addEventListener("focus", () => { sync(); sendActivity(true); });
})();
