(() => {
  let lastActivity = 0;
  let focusBlocker = null;
  const ANKI_UNLOCK_PREFIX = "ankiEntertainmentUnlocked:";

  function localDateKey() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function classify() {
    const host = location.hostname;
    const path = location.pathname;
    if (/bilibili\.com|youtube\.com|douyin\.com/.test(host)) {
      return { category: "distraction", source: host };
    }
    if (/freetcf\.com/.test(host) && path.startsWith("/question")) {
      return { category: "reading", source: "freetcf-reading" };
    }
    if (/lingua\.com/.test(host) && path.startsWith("/french/reading")) {
      return { category: "reading", source: "lingua-reading" };
    }
    if (/chatgpt\.com|chat\.openai\.com/.test(host)) {
      return { category: "contextual", source: "chatgpt" };
    }
    return null;
  }

  async function dailyTasksComplete() {
    const unlockKey = ANKI_UNLOCK_PREFIX + localDateKey();
    try {
      const stored = await chrome.storage.local.get(unlockKey);
      if (stored[unlockKey]) {
        return { complete: true, persisted: true };
      }
      const status = await fetch(
        `http://127.0.0.1:8765/api/anki-daily-status?t=${Date.now()}`
      ).then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      });
      if (status.complete) {
        await chrome.storage.local.set({ [unlockKey]: true });
      }
      return status;
    } catch (error) {
      return {
        available: false,
        complete: false,
        message: String(error?.message || error)
      };
    }
  }

  function suppressMedia() {
    document.querySelectorAll("video, audio").forEach(media => {
      if (!media.dataset.studyOriginalMuted) {
        media.dataset.studyOriginalMuted = media.muted ? "1" : "0";
        media.dataset.studyOriginalVolume = String(media.volume);
      }
      media.muted = true;
      media.volume = 0;
      media.pause?.();
      media.style.filter = "blur(18px) grayscale(1) brightness(.2)";
    });
  }

  function restoreMedia() {
    document.querySelectorAll("video, audio").forEach(media => {
      if (media.dataset.studyOriginalMuted) {
        media.muted = media.dataset.studyOriginalMuted === "1";
        const originalVolume = Number(media.dataset.studyOriginalVolume);
        media.volume = Number.isFinite(originalVolume) ? originalVolume : 1;
        delete media.dataset.studyOriginalMuted;
        delete media.dataset.studyOriginalVolume;
      }
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
      <div>
        <div style="font-size:42px;font-weight:900;line-height:1.05;margin-bottom:18px">今天的 Anki 还没有清空</div>
        <div style="font-size:20px;line-height:1.55;max-width:760px;margin:0 auto 22px">
          Bilibili / YouTube / 抖音已暂停。完成统一卡组今天的全部新卡、学习中卡片和复习卡后自动解锁。
        </div>
        <div id="study-focus-status" style="font-size:16px;opacity:.9">正在检查 Anki...</div>
      </div>
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
    const statusInfo = await dailyTasksComplete();
    if (statusInfo.complete) {
      hideWarning();
      return;
    }
    showWarning();
    const status = document.getElementById("study-focus-status");
    if (!status) return;
    if (!statusInfo.available) {
      status.textContent = "请打开 Anki。完成后当天会保持解锁，即使随后关闭 Anki。";
      return;
    }
    status.textContent = `剩余：新卡 ${Number(statusInfo.new || 0)} · 学习中 ${Number(statusInfo.learning || 0)} · 复习 ${Number(statusInfo.review || 0)}`;
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

  sendActivity(true);
  enforceDistractionBlock();
  setInterval(sendActivity, 10000);
  setInterval(enforceDistractionBlock, 3000);
  document.addEventListener("click", () => {
    setTimeout(() => sendActivity(true), 800);
  }, true);
  window.addEventListener("focus", () => sendActivity(true));
})();
