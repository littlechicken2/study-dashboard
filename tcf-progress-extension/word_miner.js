(() => {
  const CONTEXT_KEY = "tcfWordMiningContext";
  const DICTIONARY_HOST = "www.frdic.com";
  const ANKI_URL = "http://127.0.0.1:8766";
  const TARGET_DECK = "French Daily Audio + Reading";
  const MODEL_NAME = "French Chinese English Simple";
  const BUBBLE_ID = "tcf-anki-selection-bubble";
  const PANEL_ID = "tcf-anki-dictionary-panel";
  let bubbleTimer = 0;

  const clean = value => String(value || "").replace(/\s+/g, " ").trim();
  const escapeRegex = value => String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const escapeHtml = value => clean(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);
  const directText = element => clean(
    [...(element?.childNodes || [])]
      .filter(node => node.nodeType === Node.TEXT_NODE)
      .map(node => node.textContent)
      .join(" ")
  );

  function selectedFrench() {
    const value = clean(window.getSelection()?.toString())
      .replace(/^[^\p{L}À-ÿŒœÆæ'-]+|[^\p{L}À-ÿŒœÆæ'-]+$/gu, "");
    if (!value || value.length > 60 || !/[\p{L}À-ÿŒœÆæ]/u.test(value)) return "";
    return value;
  }

  function removeBubble() {
    document.getElementById(BUBBLE_ID)?.remove();
  }

  function cancelBubbleTimer() {
    if (!bubbleTimer) return;
    clearTimeout(bubbleTimer);
    bubbleTimer = 0;
  }

  async function openDictionary(word) {
    const params = new URLSearchParams(location.search);
    const context = {
      word,
      sourceUrl: location.href,
      sourceTitle: document.title,
      paperId: params.get("paperId") || "",
      questionNumber: params.get("qnumber") || "",
      capturedAt: Date.now()
    };
    let storing = null;
    try {
      storing = chrome.storage.local.set({ [CONTEXT_KEY]: context });
    } catch (_) {
      // A recently reloaded extension must not prevent the dictionary from opening.
    }
    window.open(`https://${DICTIONARY_HOST}/dicts/fr/${encodeURIComponent(word)}`, "_blank", "noopener");
    if (storing) {
      try {
        await storing;
      } catch (_) {
        // The dictionary lookup still works without the optional source context.
      }
    }
    removeBubble();
  }

  function showSelectionBubble(event) {
    const word = selectedFrench();
    removeBubble();
    if (!word) return;

    const bubble = document.createElement("div");
    bubble.id = BUBBLE_ID;
    bubble.innerHTML = `
      <span>${escapeHtml(word)}</span>
      <button type="button" title="在法语助手中查词">查词</button>
    `;
    Object.assign(bubble.style, {
      position: "fixed",
      zIndex: "2147483647",
      left: `${Math.min(event.clientX + 8, window.innerWidth - 210)}px`,
      top: `${Math.min(event.clientY + 10, window.innerHeight - 54)}px`,
      display: "flex",
      alignItems: "center",
      gap: "9px",
      maxWidth: "240px",
      padding: "7px 8px 7px 11px",
      border: "1px solid #62d9de",
      borderRadius: "4px",
      background: "#07120f",
      color: "#f3f7f5",
      boxShadow: "0 8px 28px rgba(0,0,0,.32)",
      font: "600 14px/1.2 Inter, system-ui, sans-serif"
    });
    const label = bubble.querySelector("span");
    Object.assign(label.style, {
      overflow: "hidden",
      textOverflow: "ellipsis",
      whiteSpace: "nowrap"
    });
    const button = bubble.querySelector("button");
    Object.assign(button.style, {
      border: "0",
      borderRadius: "3px",
      padding: "6px 10px",
      background: "#69e39d",
      color: "#04110c",
      fontWeight: "800",
      cursor: "pointer"
    });
    button.addEventListener("click", () => openDictionary(word));
    document.documentElement.appendChild(bubble);
  }

  async function anki(action, params = {}) {
    const response = await fetch(ANKI_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, version: 6, params })
    });
    if (!response.ok) throw new Error(`AnkiConnect HTTP ${response.status}`);
    const payload = await response.json();
    if (payload.error) throw new Error(payload.error);
    return payload.result;
  }

  function dictionaryEntry() {
    const word = clean(document.querySelector(".explain-Word .word")?.textContent);
    const ipa = directText(document.querySelector(".Phonitic"));
    const partOfSpeech = clean(document.querySelector("#ExpFCchild .cara")?.textContent);
    const meanings = [...document.querySelectorAll("#ExpFCchild .exp")]
      .map(element => clean(element.textContent))
      .filter(Boolean)
      .slice(0, 4);
    const examples = [...document.querySelectorAll("#ExpFCchild .eg")]
      .map(element => clean(element.textContent))
      .filter(Boolean)
      .slice(0, 2);
    return { word, ipa, partOfSpeech, meanings, examples };
  }

  function sourceLabel(context) {
    if (!context) return "FreeTCF 阅读";
    const pieces = [];
    if (context.paperId) pieces.push(context.paperId);
    if (context.questionNumber) pieces.push(`第 ${context.questionNumber} 题`);
    return pieces.length ? `FreeTCF ${pieces.join(" · ")}` : "FreeTCF 阅读";
  }

  async function addEntryToAnki(entry, editedMeaning, context, status, button) {
    const meaning = String(editedMeaning || "").trim();
    if (!entry.word || !meaning) {
      status.textContent = "请填写中文释义后再加入 Anki。";
      return;
    }
    button.disabled = true;
    status.textContent = "正在连接 Anki…";

    try {
      await anki("version");
      await anki("createDeck", { deck: TARGET_DECK });
      const exact = escapeRegex(entry.word);
      const existing = new Set([
        ...await anki("findNotes", { query: `French:re:^${exact}$` }),
        ...await anki("findNotes", { query: `Word:re:^${exact}$` })
      ]);
      if (existing.size) {
        const cards = await anki("findCards", { query: `nid:${[...existing].join(",")}` });
        if (cards.length) await anki("setDueDate", { cards, days: "1" });
        status.textContent = "这个词已在 Anki 中，已安排明天复习。";
        button.textContent = "已安排";
        return;
      }
      const sourceUrl = context?.sourceUrl || "https://www.freetcf.com/";
      const dictionaryUrl = location.href;
      const chinese = [
        escapeHtml(entry.partOfSpeech),
        escapeHtml(meaning).replace(/\r?\n/g, "<br>"),
        entry.ipa ? `音标 ${escapeHtml(entry.ipa)}` : ""
      ].filter(Boolean).join("<br>");
      const exampleHtml = entry.examples.length
        ? `<div>${entry.examples.map(escapeHtml).join("<br>")}</div>`
        : "";
      const sentence = `
        ${exampleHtml}
        <div style="margin-top:8px">
          <a href="${escapeHtml(sourceUrl)}">${escapeHtml(sourceLabel(context))}</a>
          · <a href="${escapeHtml(dictionaryUrl)}">法语助手词典</a>
        </div>
      `;
      const noteId = await anki("addNote", {
        note: {
          deckName: TARGET_DECK,
          modelName: MODEL_NAME,
          fields: {
            French: entry.word,
            Chinese: chinese,
            English: "",
            Sentence: sentence
          },
          options: {
            allowDuplicate: false,
            duplicateScope: "deck",
            duplicateScopeOptions: {
              deckName: TARGET_DECK,
              checkChildren: true,
              checkAllModels: false
            }
          },
          tags: [
            "TCF_Reading",
            "FreeTCF",
            "merge_source_tcf_reading",
            `mined_${new Date().toISOString().slice(0, 10).replaceAll("-", "_")}`
          ]
        }
      });
      const cards = await anki("findCards", { query: `nid:${noteId}` });
      if (cards.length) await anki("setDueDate", { cards, days: "1" });
      status.textContent = "已加入 Anki，明天进入复习。";
      button.textContent = "已加入";
    } catch (error) {
      const message = String(error?.message || error);
      if (/duplicate/i.test(message)) {
        status.textContent = "这个词已经在统一学习牌组中。";
        button.textContent = "已经存在";
      } else if (/fetch|network|failed/i.test(message)) {
        status.textContent = "请先打开 Anki，再点击一次。";
        button.disabled = false;
      } else {
        status.textContent = `加入失败：${message}`;
        button.disabled = false;
      }
    }
  }

  async function showDictionaryPanel() {
    if (document.getElementById(PANEL_ID)) return;
    const entry = dictionaryEntry();
    if (!entry.word) return;
    const stored = await chrome.storage.local.get(CONTEXT_KEY);
    const context = stored[CONTEXT_KEY];
    const recentContext = context && Date.now() - Number(context.capturedAt || 0) < 30 * 60 * 1000
      ? context
      : null;

    const panel = document.createElement("aside");
    panel.id = PANEL_ID;
    panel.innerHTML = `
      <button class="tcf-close" type="button" title="关闭">×</button>
      <div class="tcf-eyebrow">${escapeHtml(sourceLabel(recentContext))}</div>
      <div class="tcf-word">${escapeHtml(entry.word)}</div>
      <div class="tcf-meta">${escapeHtml([entry.ipa, entry.partOfSpeech].filter(Boolean).join(" · "))}</div>
      <label class="tcf-meaning-label" for="tcf-meaning-editor">中文释义（可修改）</label>
      <textarea class="tcf-meaning" id="tcf-meaning-editor" rows="5">${escapeHtml(entry.meanings.join("；"))}</textarea>
      <button class="tcf-add" type="button">加入 Anki · 明天复习</button>
      <div class="tcf-status">默认释义来自当前词典页，加入前可以直接修改。</div>
    `;
    Object.assign(panel.style, {
      position: "fixed",
      zIndex: "2147483647",
      top: "88px",
      right: "18px",
      width: "min(350px, calc(100vw - 24px))",
      padding: "16px",
      border: "1px solid #294238",
      borderRadius: "6px",
      background: "#07120f",
      color: "#f3f7f5",
      boxShadow: "0 18px 52px rgba(0,0,0,.38)",
      font: "14px/1.45 Inter, system-ui, sans-serif"
    });
    const closeButton = panel.querySelector(".tcf-close");
    Object.assign(closeButton.style, {
      position: "absolute",
      top: "8px",
      right: "8px",
      width: "28px",
      height: "28px",
      border: "0",
      background: "transparent",
      color: "#9fb1a8",
      fontSize: "22px",
      cursor: "pointer"
    });
    Object.assign(panel.querySelector(".tcf-eyebrow").style, {
      color: "#62d9de",
      fontSize: "11px",
      fontWeight: "800"
    });
    Object.assign(panel.querySelector(".tcf-word").style, {
      marginTop: "4px",
      fontSize: "28px",
      fontWeight: "900"
    });
    Object.assign(panel.querySelector(".tcf-meta").style, {
      color: "#9fb1a8",
      fontSize: "12px"
    });
    Object.assign(panel.querySelector(".tcf-meaning-label").style, {
      display: "block",
      marginTop: "12px",
      color: "#c8d7d0",
      fontSize: "12px",
      fontWeight: "700"
    });
    Object.assign(panel.querySelector(".tcf-meaning").style, {
      boxSizing: "border-box",
      width: "100%",
      minHeight: "104px",
      margin: "6px 0 12px",
      padding: "10px",
      border: "1px solid #294238",
      borderRadius: "4px",
      outline: "none",
      resize: "vertical",
      background: "#10211b",
      color: "#f3f7f5",
      font: "600 14px/1.45 Inter, system-ui, sans-serif"
    });
    const meaningEditor = panel.querySelector(".tcf-meaning");
    meaningEditor.addEventListener("focus", () => {
      meaningEditor.style.borderColor = "#62d9de";
    });
    meaningEditor.addEventListener("blur", () => {
      meaningEditor.style.borderColor = "#294238";
    });
    const addButton = panel.querySelector(".tcf-add");
    Object.assign(addButton.style, {
      width: "100%",
      minHeight: "40px",
      border: "0",
      borderRadius: "4px",
      background: "#69e39d",
      color: "#04110c",
      fontWeight: "900",
      cursor: "pointer"
    });
    const status = panel.querySelector(".tcf-status");
    Object.assign(status.style, {
      marginTop: "8px",
      color: "#9fb1a8",
      fontSize: "11px"
    });
    closeButton.addEventListener("click", () => panel.remove());
    addButton.addEventListener("click", () => (
      addEntryToAnki(entry, meaningEditor.value, recentContext, status, addButton)
    ));
    document.documentElement.appendChild(panel);
  }

  if (location.hostname === DICTIONARY_HOST) {
    const observer = new MutationObserver(() => {
      if (document.querySelector(".explain-Word .word") && document.querySelector("#ExpFCchild .exp")) {
        observer.disconnect();
        showDictionaryPanel();
      }
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    showDictionaryPanel();
    return;
  }

  document.addEventListener("mouseup", event => {
    if (event.target instanceof Element && event.target.closest(`#${BUBBLE_ID}`)) return;
    cancelBubbleTimer();
    if (event.detail > 1) return;
    bubbleTimer = setTimeout(() => {
      bubbleTimer = 0;
      showSelectionBubble(event);
    }, 420);
  }, true);
  document.addEventListener("dblclick", () => {
    cancelBubbleTimer();
    removeBubble();
    const word = selectedFrench();
    if (word) openDictionary(word);
  }, true);
  document.addEventListener("mousedown", event => {
    if (event.target instanceof Element && !event.target.closest(`#${BUBBLE_ID}`)) removeBubble();
  }, true);
  window.addEventListener("blur", () => {
    cancelBubbleTimer();
    removeBubble();
  });
})();
