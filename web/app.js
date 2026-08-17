const config = window.APP_CONFIG || {};
const state = {
  contests: [],
  query: "",
  category: "all",
  ai: "active",
  sort: "deadline",
};

const els = {
  cards: document.querySelector("#cards"),
  search: document.querySelector("#searchInput"),
  chips: document.querySelector("#categoryChips"),
  aiFilter: document.querySelector("#aiFilter"),
  sort: document.querySelector("#sortSelect"),
  count: document.querySelector("#resultCount"),
  heroStat: document.querySelector("#heroStat strong"),
  empty: document.querySelector("#emptyState"),
  error: document.querySelector("#errorState"),
  errorMessage: document.querySelector("#errorMessage"),
};

const AI_LABELS = {
  required: "AI 필수",
  allowed: "AI 가능",
  restricted: "조건부",
  prohibited: "AI 금지",
  unknown: "확인 필요",
};

const CATEGORY_LABELS = {
  image: "🎨 그림",
  video: "🎬 영상",
  writing: "✍️ 글",
  music: "🎵 음악",
  other: "✨ 기타",
};

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "미정";
  const d = new Date(`${value}T00:00:00`);
  if (Number.isNaN(d.getTime())) return value;
  return new Intl.DateTimeFormat("ko-KR", {
    year: "numeric", month: "2-digit", day: "2-digit"
  }).format(d);
}

function dDay(value) {
  if (!value) return "D-?";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const deadline = new Date(`${value}T00:00:00`);
  const diff = Math.ceil((deadline - today) / 86400000);
  if (diff === 0) return "D-DAY";
  if (diff > 0) return `D-${diff}`;
  return `마감`;
}

function formatPrize(row) {
  if (row.prize_text) return row.prize_text;
  if (row.total_prize_won) {
    return `${Number(row.total_prize_won).toLocaleString("ko-KR")}원`;
  }
  return "미정";
}

function getFiltered() {
  const q = state.query.trim().toLowerCase();

  let rows = state.contests.filter((row) => {
    if (state.category !== "all" && !(row.categories || []).includes(state.category)) {
      return false;
    }

    if (state.ai === "active" && row.ai_requirement === "prohibited") {
      return false;
    }

    if (!["active", "all"].includes(state.ai) && row.ai_requirement !== state.ai) {
      return false;
    }

    if (q) {
      const haystack = [
        row.title, row.organizer, row.summary, row.ai_reason,
        ...(row.categories || [])
      ].filter(Boolean).join(" ").toLowerCase();
      if (!haystack.includes(q)) return false;
    }

    return true;
  });

  rows.sort((a, b) => {
    if (state.sort === "newest") {
      return new Date(b.first_seen_at || b.created_at || 0) - new Date(a.first_seen_at || a.created_at || 0);
    }

    if (state.sort === "prize") {
      return Number(b.total_prize_won || 0) - Number(a.total_prize_won || 0);
    }

    // Deadline: upcoming first, expired last, null last.
    const now = new Date();
    now.setHours(0, 0, 0, 0);

    const score = (row) => {
      if (!row.deadline) return Number.MAX_SAFE_INTEGER;
      const t = new Date(`${row.deadline}T00:00:00`).getTime();
      return t < now.getTime() ? Number.MAX_SAFE_INTEGER - 1 : t;
    };
    return score(a) - score(b);
  });

  return rows;
}

function cardTemplate(row) {
  const categories = (row.categories || [])
    .map((c) => `<span class="badge">${escapeHtml(CATEGORY_LABELS[c] || c)}</span>`)
    .join("");

  const ai = row.ai_requirement || "unknown";
  const confidence = row.ai_confidence != null
    ? `${Math.round(Number(row.ai_confidence) * 100)}%`
    : "—";

  return `
    <article class="card">
      <div class="badges">
        <span class="badge ${escapeHtml(ai)}">${escapeHtml(AI_LABELS[ai] || "확인 필요")}</span>
        ${categories}
      </div>

      <h2>${escapeHtml(row.title)}</h2>
      <p class="organizer">${escapeHtml(row.organizer || "주최사 확인 필요")}</p>

      <div class="meta">
        <div class="meta-item">
          <span>마감</span>
          <strong>${escapeHtml(formatDate(row.deadline))} · ${escapeHtml(dDay(row.deadline))}</strong>
        </div>
        <div class="meta-item">
          <span>상금</span>
          <strong>${escapeHtml(formatPrize(row))}</strong>
        </div>
      </div>

      <p class="summary">${escapeHtml(row.summary || "요약 정보 없음")}</p>
      <p class="ai-reason">AI 판정 ${confidence} · ${escapeHtml(row.ai_reason || "판정 근거 확인 필요")}</p>

      <div class="card-footer">
        <span class="source">${escapeHtml(row.source || "")}</span>
        <a class="source-link"
           href="${escapeHtml(row.source_url)}"
           target="_blank"
           rel="noopener noreferrer">원문 보기 ↗</a>
      </div>
    </article>
  `;
}

function render() {
  const rows = getFiltered();
  els.count.textContent = `${rows.length}개의 공모전`;
  els.heroStat.textContent = state.contests.filter(x => x.ai_requirement !== "prohibited").length;

  els.cards.innerHTML = rows.map(cardTemplate).join("");
  els.empty.classList.toggle("hidden", rows.length !== 0);
}

async function loadContests() {
  if (
    !config.SUPABASE_URL ||
    !config.SUPABASE_PUBLIC_KEY ||
    config.SUPABASE_URL.includes("YOUR_") ||
    config.SUPABASE_PUBLIC_KEY.includes("YOUR_")
  ) {
    throw new Error("web/config.js에 Supabase URL과 Publishable key를 입력해야 해.");
  }

  const endpoint =
    `${config.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/contests` +
    `?select=*&order=first_seen_at.desc&limit=1000`;

  const response = await fetch(endpoint, {
    headers: {
      apikey: config.SUPABASE_PUBLIC_KEY,
      Authorization: `Bearer ${config.SUPABASE_PUBLIC_KEY}`,
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Supabase ${response.status}: ${text.slice(0, 180)}`);
  }

  state.contests = await response.json();
  render();
}

els.search.addEventListener("input", (e) => {
  state.query = e.target.value;
  render();
});

els.chips.addEventListener("click", (e) => {
  const button = e.target.closest("[data-category]");
  if (!button) return;

  state.category = button.dataset.category;
  document.querySelectorAll(".chip").forEach((chip) => chip.classList.remove("active"));
  button.classList.add("active");
  render();
});

els.aiFilter.addEventListener("change", (e) => {
  state.ai = e.target.value;
  render();
});

els.sort.addEventListener("change", (e) => {
  state.sort = e.target.value;
  render();
});

loadContests().catch((error) => {
  console.error(error);
  els.count.textContent = "데이터 로드 실패";
  els.cards.innerHTML = "";
  els.empty.classList.add("hidden");
  els.error.classList.remove("hidden");
  els.errorMessage.textContent = error.message;
});
