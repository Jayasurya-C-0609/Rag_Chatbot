/* ============================================
   ContextIQ — Frontend Application Logic
   Pure Vanilla JavaScript
   ============================================ */

// -------------------------------------------------
// API Configuration
// -------------------------------------------------
const API = {
  baseUrl: "",
  endpoints: {
    health:      "/api/v1/health",
    healthReady: "/api/v1/health/ready",
    chat:        "/api/v1/chat",
    chatStream:  "/api/v1/chat/stream",
    documents:   "/api/v1/documents",
    upload:      "/api/v1/documents/upload",
    status:      "/api/v1/documents/status",
    rebuild:     "/api/v1/documents/rebuild",
    clear:       "/api/v1/documents",
  },
  url(endpoint) {
    return this.baseUrl + endpoint;
  }
};

// -------------------------------------------------
// State
// -------------------------------------------------
const state = {
  chatHistory: [],   // {role, content}
  messages: [],      // {role, content, sources}
  isStreaming: false,
  recentChats: [],
  currentChatId: null, // Track current conversation for recent chats
};

// -------------------------------------------------
// Utility Helpers
// -------------------------------------------------
function $(sel, ctx) { return (ctx || document).querySelector(sel); }
function $$(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

function escapeHtml(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function renderMarkdown(text) {
  if (!text) return "";
  
  // Escape HTML but preserve literally generated <br> tags
  let html = escapeHtml(text).replace(/&lt;br\s*\/?[&gt;]*>/gi, '<br>');

  // Bold and Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Code blocks
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');

  let lines = html.split('\n');
  let out = [];
  let inList = false;
  let inTable = false;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    // Table parsing
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      if (!inTable) {
        inTable = true;
        out.push('<div class="table-responsive"><table class="md-table" style="width:100%; border-collapse:collapse; margin:10px 0;">');
      }
      // Skip markdown separator lines
      if (line.replace(/\|/g, '').replace(/-/g, '').replace(/:/g, '').trim() === '') continue;
      
      let cells = line.split('|').map(c => c.trim());
      cells.shift(); cells.pop(); // Remove empty edges
      out.push('<tr>' + cells.map(c => '<td style="border:1px solid var(--border); padding:8px;">' + c + '</td>').join('') + '</tr>');
      continue;
    } else if (inTable) {
      inTable = false;
      out.push('</table></div>');
    }

    // List parsing
    if (line.trim().match(/^[-*]\s+(.*)/)) {
      if (!inList) {
        inList = true;
        out.push('<ul style="margin-left:20px; padding-left:0;">');
      }
      out.push('<li style="margin-bottom:4px;">' + line.trim().replace(/^[-*]\s+/, '') + '</li>');
      continue;
    } else if (inList) {
      inList = false;
      out.push('</ul>');
    }

    out.push(line);
  }

  if (inTable) out.push('</table></div>');
  if (inList) out.push('</ul>');

  // Join lines and convert loose newlines to <br>
  html = out.join('\n');
  html = html.replace(/\n/g, '<br>');
  
  // Clean up formatting artifacts
  html = html.replace(/<br><ul/g, '<ul');
  html = html.replace(/<\/ul><br>/g, '</ul>');
  html = html.replace(/<br><div class="table-responsive/g, '<div class="table-responsive');
  html = html.replace(/<\/div><br>/g, '</div>');

  return html;
}


function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 8);
}

// -------------------------------------------------
// Sidebar (shared across workspace & KB)
// -------------------------------------------------
function initSidebar() {
  const btn = $("#mobileMenuBtn");
  const sidebar = $("#sidebar");
  const overlay = $("#sidebarOverlay");
  if (!btn || !sidebar) return;

  function openSidebar() {
    sidebar.classList.add("open");
    overlay.classList.add("visible");
  }
  function closeSidebar() {
    sidebar.classList.remove("open");
    overlay.classList.remove("visible");
  }

  btn.addEventListener("click", openSidebar);
  if (overlay) overlay.addEventListener("click", closeSidebar);

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSidebar();
  });
}

function renderRecentChats() {
  const containers = $$("#recentChats");
  const saved = JSON.parse(localStorage.getItem("contextiq_recent") || "[]");
  state.recentChats = saved;

  containers.forEach(function (el) {
    el.innerHTML = "";
    if (saved.length === 0) {
      el.innerHTML = '<div style="padding:8px 12px;font-size:13px;color:var(--text-muted);">No recent chats</div>';
      return;
    }
    saved.forEach(function (chat, i) {
      var a = document.createElement("a");
      a.href = "#";
      a.className = "sidebar-link" + (chat.id === state.currentChatId ? " active" : "");
      a.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>' +
        escapeHtml(chat.title);
      a.addEventListener("click", function (e) {
        e.preventDefault();
        loadRecentChat(i);
      });
      el.appendChild(a);
    });
  });
}

function saveRecentChat(title, messages, history) {
  var saved = JSON.parse(localStorage.getItem("contextiq_recent") || "[]");

  // If we have a current chat id, update the existing entry instead of duplicating
  if (state.currentChatId) {
    var existingIdx = saved.findIndex(function(c) { return c.id === state.currentChatId; });
    if (existingIdx !== -1) {
      saved[existingIdx].messages = messages;
      saved[existingIdx].history = history;
      localStorage.setItem("contextiq_recent", JSON.stringify(saved));
      renderRecentChats();
      return;
    }
  }

  // New chat: generate an ID and push
  state.currentChatId = generateId();
  saved.unshift({ id: state.currentChatId, title: title, messages: messages, history: history });
  if (saved.length > 5) saved = saved.slice(0, 5);
  localStorage.setItem("contextiq_recent", JSON.stringify(saved));
  renderRecentChats();
}

function loadRecentChat(index) {
  var saved = JSON.parse(localStorage.getItem("contextiq_recent") || "[]");
  if (!saved[index]) return;
  if (window.location.pathname.indexOf("workspace") === -1) {
    localStorage.setItem("contextiq_load_chat", index.toString());
    window.location.href = "workspace.html";
    return;
  }
  state.messages = JSON.parse(JSON.stringify(saved[index].messages || []));
  state.chatHistory = JSON.parse(JSON.stringify(saved[index].history || []));
  state.currentChatId = saved[index].id || null;
  renderAllMessages();
  renderRecentChats();
}

// -------------------------------------------------
// Chat Workspace
// -------------------------------------------------
function initWorkspace() {
  var input = $("#chatInput");
  var sendBtn = $("#sendBtn");
  var newChatBtn = $("#newChatBtn");
  if (!input) return;

  // Auto-resize textarea
  input.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 120) + "px";
    sendBtn.disabled = !this.value.trim();
  });

  // Enter = send, Shift+Enter = newline
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (this.value.trim()) handleSend();
    }
  });

  sendBtn.addEventListener("click", function () {
    if (input.value.trim()) handleSend();
  });

  // Suggested questions
  $$(".suggested-q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      input.value = this.dataset.question;
      input.dispatchEvent(new Event("input"));
      handleSend();
    });
  });

  // New Chat
  if (newChatBtn) {
    newChatBtn.addEventListener("click", function () {
      state.messages = [];
      state.chatHistory = [];
      state.isStreaming = false;
      state.currentChatId = null;
      showEmptyState();
      renderRecentChats();
    });
  }

  // Check if we should load a recent chat (navigated from KB page)
  var pendingLoad = localStorage.getItem("contextiq_load_chat");
  if (pendingLoad !== null) {
    localStorage.removeItem("contextiq_load_chat");
    loadRecentChat(parseInt(pendingLoad, 10));
  }
}

function showEmptyState() {
  var empty = $("#emptyState");
  var msgs = $("#messagesArea");
  if (empty) empty.style.display = "flex";
  if (msgs) { msgs.style.display = "none"; msgs.innerHTML = ""; }
}

function showMessagesArea() {
  var empty = $("#emptyState");
  var msgs = $("#messagesArea");
  if (empty) empty.style.display = "none";
  if (msgs) msgs.style.display = "flex";
}

function renderAllMessages() {
  showMessagesArea();
  var area = $("#messagesArea");
  area.innerHTML = "";
  state.messages.forEach(function (msg) {
    appendMessageBubble(msg.role, msg.content, msg.sources);
  });
  scrollToBottom();
}

function appendMessageBubble(role, content, sources) {
  var area = $("#messagesArea");
  if (!area) return;

  var div = document.createElement("div");
  div.className = "msg " + (role === "user" ? "user-msg" : "ai-msg");

  var avatarSvg = role === "user"
    ? '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v2h20v-2c0-3.3-6.7-5-10-5z"/></svg>'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1010 10A10 10 0 0012 2z"/><path d="M12 6v6l4 2"/></svg>';

  var html =
    '<div class="msg-avatar">' + avatarSvg + '</div>' +
    '<div class="msg-body">' +
      '<div class="msg-bubble">' + (role === "user" ? escapeHtml(content) : renderMarkdown(content)) + '</div>';

  if (sources && sources.length > 0) {
    sources.forEach(function (src) {
      var label = "Grounded in: " + escapeHtml(src.file_name);
      if (src.page != null) label += ", Page " + src.page;
      html +=
        '<div class="msg-source">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>' +
          label +
        '</div>';
    });
  }

  html += '</div>';
  div.innerHTML = html;
  area.appendChild(div);
}

function appendTypingIndicator() {
  var area = $("#messagesArea");
  if (!area) return;
  var div = document.createElement("div");
  div.className = "msg ai-msg";
  div.id = "typingIndicator";
  div.innerHTML =
    '<div class="msg-avatar"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1010 10A10 10 0 0012 2z"/><path d="M12 6v6l4 2"/></svg></div>' +
    '<div class="msg-body">' +
      '<div class="typing-indicator">' +
        '<div class="typing-dots"><span></span><span></span><span></span></div>' +
        '<span class="typing-text" id="typingText">Searching available documents...</span>' +
      '</div>' +
    '</div>';
  area.appendChild(div);
  scrollToBottom();
}

function removeTypingIndicator() {
  var el = $("#typingIndicator");
  if (el) el.remove();
}

function appendStreamingBubble(streamId) {
  var area = $("#messagesArea");
  if (!area) return;
  var div = document.createElement("div");
  div.className = "msg ai-msg";
  div.id = "streamingMsg-" + streamId;
  div.innerHTML =
    '<div class="msg-avatar"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1010 10A10 10 0 0012 2z"/><path d="M12 6v6l4 2"/></svg></div>' +
    '<div class="msg-body">' +
      '<div class="msg-bubble" id="streamingContent-' + streamId + '"></div>' +
      '<div id="streamingSources-' + streamId + '"></div>' +
    '</div>';
  area.appendChild(div);
  scrollToBottom();
}

function scrollToBottom() {
  var area = $("#messagesArea");
  if (area) area.scrollTop = area.scrollHeight;
}

async function handleSend() {
  var input = $("#chatInput");
  var question = input.value.trim();
  if (!question || state.isStreaming) return;

  // Clear input
  input.value = "";
  input.style.height = "auto";
  $("#sendBtn").disabled = true;
  state.isStreaming = true;

  // Show messages area
  showMessagesArea();

  // Add user message
  state.messages.push({ role: "user", content: question, sources: [] });
  appendMessageBubble("user", question, []);
  scrollToBottom();

  // Show typing
  appendTypingIndicator();

  try {
    // Use streaming endpoint
    var body = JSON.stringify({
      question: question,
      chat_history: state.chatHistory
    });

    var response = await fetch(API.url(API.endpoints.chatStream), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body
    });

    if (!response.ok) {
      var errBody;
      try { errBody = await response.json(); } catch(e) { errBody = null; }
      var errMsg = (errBody && errBody.error && errBody.error.message)
        ? errBody.error.message
        : "Server error: " + response.status;
      throw new Error(errMsg);
    }

    // Generate unique ID for this streaming session to prevent overriding old messages
    var currentStreamId = generateId();
    var streamingBubbleCreated = false;

    var reader = response.body.getReader();
    var decoder = new TextDecoder();
    var fullAnswer = "";
    var sources = [];
    var buffer = "";

    while (true) {
      var result = await reader.read();
      if (result.done) break;

      buffer += decoder.decode(result.value, { stream: true });
      var lines = buffer.split("\n");
      buffer = lines.pop(); // keep incomplete line

      var eventType = null;
      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.startsWith("event: ")) {
          eventType = line.substring(7).trim();
        } else if (line.startsWith("data: ") && eventType) {
          var dataStr = line.substring(6);
          var data;
          try {
            data = JSON.parse(dataStr);
          } catch (e) {
            data = dataStr;
          }

          if (eventType === "status") {
            // Update typing indicator text if it's still showing
            var tt = $("#typingText");
            if (tt) tt.textContent = data || "Generating grounded answer...";
          } else if (eventType === "token") {
            // On first token, swap typing indicator for streaming bubble
            if (!streamingBubbleCreated) {
              removeTypingIndicator();
              appendStreamingBubble(currentStreamId);
              streamingBubbleCreated = true;
            }
            fullAnswer += data;
            var sc = $("#streamingContent-" + currentStreamId);
            if (sc) sc.innerHTML = renderMarkdown(fullAnswer);
            scrollToBottom();
          } else if (eventType === "source") {
            sources = data;
            // Ensure streaming bubble exists
            if (!streamingBubbleCreated) {
              removeTypingIndicator();
              appendStreamingBubble(currentStreamId);
              streamingBubbleCreated = true;
            }
            var sd = $("#streamingSources-" + currentStreamId);
            if (sd && Array.isArray(sources)) {
              sd.innerHTML = "";
              sources.forEach(function (src) {
                var label = "Grounded in: " + escapeHtml(src.file_name);
                if (src.page != null) label += ", Page " + src.page;
                sd.innerHTML +=
                  '<div class="msg-source">' +
                    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>' +
                    label +
                  '</div>';
              });
            }
          } else if (eventType === "done") {
            // Stream completed
          } else if (eventType === "error") {
            if (!streamingBubbleCreated) {
              removeTypingIndicator();
              appendStreamingBubble(currentStreamId);
              streamingBubbleCreated = true;
            }
            fullAnswer = "An error occurred: " + data;
            var sc2 = $("#streamingContent-" + currentStreamId);
            if (sc2) sc2.innerHTML = renderMarkdown(fullAnswer);
          }
          eventType = null;
        }
      }
    }

    // If no tokens were received at all (edge case), still clean up
    if (!streamingBubbleCreated) {
      removeTypingIndicator();
      if (!fullAnswer) {
        fullAnswer = "No response received.";
      }
      appendMessageBubble("assistant", fullAnswer, sources);
    }

    // Store message
    state.messages.push({ role: "assistant", content: fullAnswer, sources: sources });
    state.chatHistory.push({ role: "user", content: question });
    state.chatHistory.push({ role: "assistant", content: fullAnswer });

    // Save to recent chats (updates existing or creates new)
    var chatTitle = state.messages.length > 0 && state.messages[0].role === "user"
      ? state.messages[0].content
      : question;
    if (chatTitle.length > 30) chatTitle = chatTitle.substring(0, 30) + "...";
    saveRecentChat(chatTitle, state.messages, state.chatHistory);

  } catch (err) {
    removeTypingIndicator();
    var errorContent = "Failed to get a response. " + (err.message || "Please check if the backend is running.");
    appendMessageBubble("assistant", errorContent, []);
    state.messages.push({ role: "assistant", content: errorContent, sources: [] });
  }

  state.isStreaming = false;
  scrollToBottom();
}


// -------------------------------------------------
// Knowledge Base
// -------------------------------------------------
function initKnowledgeBase() {
  var uploadZone = $("#uploadZone");
  var fileInput = $("#fileInput");
  var uploadTrigger = $("#uploadTrigger");
  if (!uploadZone) return;

  // Click to upload
  uploadZone.addEventListener("click", function (e) {
    // Don't trigger if the Browse Files button was clicked (it has its own handler)
    if (e.target.closest(".browse-btn")) return;
    fileInput.click();
  });
  if (uploadTrigger) uploadTrigger.addEventListener("click", function (e) {
    e.stopPropagation();
    fileInput.click();
  });

  // Browse Files button inside upload zone
  var browseBtn = $(".browse-btn", uploadZone);
  if (browseBtn) {
    browseBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      fileInput.click();
    });
  }

  // Keyboard accessible
  uploadZone.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); }
  });

  // Drag & Drop
  uploadZone.addEventListener("dragover", function (e) { e.preventDefault(); this.classList.add("drag-over"); });
  uploadZone.addEventListener("dragleave", function () { this.classList.remove("drag-over"); });
  uploadZone.addEventListener("drop", function (e) {
    e.preventDefault();
    this.classList.remove("drag-over");
    handleFiles(e.dataTransfer.files);
  });

  // File input change
  fileInput.addEventListener("change", function () {
    handleFiles(this.files);
    this.value = "";
  });

  // Search
  var search = $("#docSearch");
  if (search) {
    search.addEventListener("input", function () {
      filterDocuments(this.value.trim().toLowerCase());
    });
  }

  // Rebuild
  var rebuildBtn = $("#rebuildBtn");
  if (rebuildBtn) {
    rebuildBtn.addEventListener("click", function () {
      showModal("rebuildModal");
    });
  }

  // Clear
  var clearBtn = $("#clearBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      showModal("clearModal");
    });
  }

  // Modal: Delete
  var deleteCancelBtn = $("#deleteCancelBtn");
  var deleteConfirmBtn = $("#deleteConfirmBtn");
  if (deleteCancelBtn) deleteCancelBtn.addEventListener("click", function () { hideModal("deleteModal"); });
  if (deleteConfirmBtn) deleteConfirmBtn.addEventListener("click", confirmDelete);

  // Modal: Clear
  var clearCancelBtn = $("#clearCancelBtn");
  var clearConfirmBtn = $("#clearConfirmBtn");
  if (clearCancelBtn) clearCancelBtn.addEventListener("click", function () { hideModal("clearModal"); });
  if (clearConfirmBtn) clearConfirmBtn.addEventListener("click", confirmClear);

  // Modal: Rebuild
  var rebuildCancelBtn = $("#rebuildCancelBtn");
  var rebuildConfirmBtn = $("#rebuildConfirmBtn");
  if (rebuildCancelBtn) rebuildCancelBtn.addEventListener("click", function () { hideModal("rebuildModal"); });
  if (rebuildConfirmBtn) rebuildConfirmBtn.addEventListener("click", confirmRebuild);

  // Close modals on Escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      hideModal("deleteModal");
      hideModal("clearModal");
      hideModal("rebuildModal");
    }
  });

  // Close modals on overlay click
  $$(".modal-overlay").forEach(function(overlay) {
    overlay.addEventListener("click", function(e) {
      if (e.target === overlay) {
        overlay.classList.remove("visible");
      }
    });
  });

  // Load documents
  loadDocuments();
}

var pendingDeleteFile = null;

function showModal(id) {
  var m = document.getElementById(id);
  if (m) m.classList.add("visible");
}
function hideModal(id) {
  var m = document.getElementById(id);
  if (m) m.classList.remove("visible");
}

async function handleFiles(files) {
  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showNotification("Only PDF files are supported.", "error");
      continue;
    }
    await uploadFile(file);
  }
}

// Notification helper
function showNotification(msg, type) {
  var existing = $("#notification-toast");
  if (existing) existing.remove();

  var toast = document.createElement("div");
  toast.id = "notification-toast";
  toast.style.cssText =
    "position:fixed;top:20px;right:20px;z-index:200;padding:12px 20px;" +
    "border-radius:8px;font-size:14px;font-weight:500;color:#fff;" +
    "box-shadow:0 4px 12px rgba(0,0,0,0.15);transition:opacity 0.3s;" +
    "background:" + (type === "error" ? "#c62828" : type === "success" ? "#2e7d32" : "#4b41e1") + ";";
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(function() {
    toast.style.opacity = "0";
    setTimeout(function() { toast.remove(); }, 300);
  }, 3000);
}

async function uploadFile(file) {
  var area = $("#uploadProgressArea");
  var progressEl = document.createElement("div");
  progressEl.className = "upload-progress";
  progressEl.innerHTML =
    '<div class="file-info">' +
      '<div class="file-name">' + escapeHtml(file.name) + '</div>' +
      '<div class="progress-bar"><div class="progress-fill" style="width:0%"></div></div>' +
    '</div>' +
    '<div class="upload-status">Uploading...</div>';
  area.appendChild(progressEl);

  var fill = $(".progress-fill", progressEl);
  var statusEl = $(".upload-status", progressEl);

  try {
    fill.style.width = "30%";
    var formData = new FormData();
    formData.append("file", file);

    statusEl.textContent = "Uploading & indexing...";
    fill.style.width = "50%";

    var resp = await fetch(API.url(API.endpoints.upload), {
      method: "POST",
      body: formData
    });

    fill.style.width = "80%";

    if (!resp.ok) {
      var errData;
      try { errData = await resp.json(); } catch(e) { errData = null; }
      var errMsg = (errData && errData.error && errData.error.message)
        ? errData.error.message
        : (errData && errData.detail) ? errData.detail : "Upload failed";
      throw new Error(errMsg);
    }

    fill.style.width = "100%";
    statusEl.textContent = "Indexed";
    statusEl.style.color = "var(--success)";
    showNotification("Document uploaded and indexed successfully.", "success");

    setTimeout(function () { progressEl.remove(); }, 2000);
    loadDocuments();

  } catch (err) {
    fill.style.width = "100%";
    fill.style.background = "var(--danger)";
    statusEl.textContent = "Failed: " + err.message;
    statusEl.style.color = "var(--danger)";
    showNotification("Upload failed: " + err.message, "error");
    setTimeout(function () { progressEl.remove(); }, 4000);
  }
}

async function loadDocuments() {
  try {
    var resp = await fetch(API.url(API.endpoints.documents));
    if (!resp.ok) throw new Error("Failed to fetch documents");
    var data = await resp.json();

    var docs = data.documents || [];
    var tbody = $("#docsTableBody");
    var statAvail = $("#statDocsAvailable");
    var statIndexed = $("#statDocsIndexed");
    var statStatus = $("#statKbStatus");

    if (statAvail) statAvail.textContent = docs.length;
    if (statIndexed) statIndexed.textContent = docs.length;
    if (statStatus) {
      statStatus.textContent = docs.length > 0 ? "Ready" : "Empty";
      statStatus.style.color = "";
    }

    if (!tbody) return;

    if (docs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="docs-empty">No documents uploaded yet. Upload a PDF to get started.</td></tr>';
      return;
    }

    tbody.innerHTML = "";
    docs.forEach(function (doc) {
      var tr = document.createElement("tr");
      tr.dataset.name = doc.file_name.toLowerCase();
      tr.innerHTML =
        '<td><div class="doc-name">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="#c62828" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>' +
          escapeHtml(doc.file_name) +
        '</div></td>' +
        '<td>' + new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) + '</td>' +
        '<td>--</td>' +
        '<td><span class="status-badge indexed"><span class="status-dot"></span> Indexed &middot; Ready</span></td>' +
        '<td>' +
          '<button class="delete-btn" data-file="' + escapeHtml(doc.file_name) + '" aria-label="Delete ' + escapeHtml(doc.file_name) + '">' +
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>' +
          '</button>' +
        '</td>';
      tbody.appendChild(tr);
    });

    // Attach delete handlers
    $$(".delete-btn", tbody).forEach(function (btn) {
      btn.addEventListener("click", function () {
        pendingDeleteFile = this.dataset.file;
        var msg = $("#deleteModalMsg");
        if (msg) msg.textContent = 'Are you sure you want to delete "' + pendingDeleteFile + '"? This action cannot be undone.';
        showModal("deleteModal");
      });
    });

  } catch (err) {
    var tbody2 = $("#docsTableBody");
    if (tbody2) tbody2.innerHTML = '<tr><td colspan="5" class="docs-empty">Could not load documents. Is the backend running?</td></tr>';
    var statStatus2 = $("#statKbStatus");
    if (statStatus2) { statStatus2.textContent = "Offline"; statStatus2.style.color = "var(--danger)"; }
  }
}

function filterDocuments(query) {
  var rows = $$("#docsTableBody tr");
  rows.forEach(function (tr) {
    if (!tr.dataset.name) { tr.style.display = ""; return; }
    tr.style.display = tr.dataset.name.indexOf(query) !== -1 ? "" : "none";
  });
}

async function confirmDelete() {
  if (!pendingDeleteFile) return;
  hideModal("deleteModal");

  try {
    var resp = await fetch(API.url(API.endpoints.documents) + "/" + encodeURIComponent(pendingDeleteFile), {
      method: "DELETE"
    });
    if (!resp.ok) {
      var errData;
      try { errData = await resp.json(); } catch(e) { errData = null; }
      throw new Error((errData && errData.error && errData.error.message) ? errData.error.message : "Delete failed");
    }
    showNotification('"' + pendingDeleteFile + '" deleted successfully.', "success");
    loadDocuments();
  } catch (err) {
    showNotification("Failed to delete: " + err.message, "error");
  }
  pendingDeleteFile = null;
}

async function confirmClear() {
  hideModal("clearModal");
  var statStatus = $("#statKbStatus");
  if (statStatus) { statStatus.textContent = "Clearing..."; statStatus.style.color = "var(--warning)"; }

  try {
    var resp = await fetch(API.url(API.endpoints.clear), { method: "DELETE" });
    if (!resp.ok) throw new Error("Clear failed");
    showNotification("Knowledge base cleared.", "success");
    loadDocuments();
  } catch (err) {
    if (statStatus) { statStatus.textContent = "Error"; statStatus.style.color = "var(--danger)"; }
    showNotification("Failed to clear knowledge base: " + err.message, "error");
  }
}

async function confirmRebuild() {
  hideModal("rebuildModal");
  var statStatus = $("#statKbStatus");
  if (statStatus) { statStatus.textContent = "Rebuilding..."; statStatus.style.color = "var(--warning)"; }

  try {
    var resp = await fetch(API.url(API.endpoints.rebuild), { method: "POST" });
    if (!resp.ok) throw new Error("Rebuild failed");
    showNotification("Knowledge base rebuilt successfully.", "success");
    if (statStatus) { statStatus.textContent = "Ready"; statStatus.style.color = ""; }
    loadDocuments();
  } catch (err) {
    if (statStatus) { statStatus.textContent = "Error"; statStatus.style.color = "var(--danger)"; }
    showNotification("Failed to rebuild: " + err.message, "error");
  }
}


// -------------------------------------------------
// Init
// -------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  initSidebar();
  renderRecentChats();
  initWorkspace();
  initKnowledgeBase();
});
