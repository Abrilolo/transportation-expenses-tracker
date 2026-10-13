(function () {
  const data = window.TRANSPORTATION_DASHBOARD_DATA || {
    generatedAt: null,
    cards: [],
    scans: [],
    transactions: [],
  };

  const defaultCardId = data.cards?.[0]?.cardId || "";

  const state = {
    cardId: defaultCardId,
    type: "all",
    from: "",
    to: "",
    showAllTransactions: false,
  };

  const elements = {
    lastUpdated: document.getElementById("lastUpdated"),
    resetFilters: document.getElementById("resetFilters"),
    cardFilter: document.getElementById("cardFilter"),
    typeFilter: document.getElementById("typeFilter"),
    fromDate: document.getElementById("fromDate"),
    toDate: document.getElementById("toDate"),
    totalExpense: document.getElementById("totalExpense"),
    latestBalance: document.getElementById("latestBalance"),
    transactionCount: document.getElementById("transactionCount"),
    topStation: document.getElementById("topStation"),
    cardPreviewLabel: document.getElementById("cardPreviewLabel"),
    cardPreviewBalance: document.getElementById("cardPreviewBalance"),
    dailyChart: document.getElementById("dailyChart"),
    typeChart: document.getElementById("typeChart"),
    stationChart: document.getElementById("stationChart"),
    scanStats: document.getElementById("scanStats"),
    scanSummary: document.getElementById("scanSummary"),
    transactionsTable: document.getElementById("transactionsTable"),
    tableSummary: document.getElementById("tableSummary"),
    toggleTransactions: document.getElementById("toggleTransactions"),
  };

  function formatYen(value) {
    const amount = Number(value || 0);
    return `¥${amount.toLocaleString("en-US")}`;
  }

  function formatSignedYen(value) {
    const amount = Number(value || 0);
    if (amount > 0) return `+${formatYen(amount)}`;
    if (amount < 0) return `-${formatYen(Math.abs(amount))}`;
    return formatYen(0);
  }

  function setOptions(select, options, selectedValue) {
    select.innerHTML = "";
    options.forEach((option) => {
      const element = document.createElement("option");
      element.value = option.value;
      element.textContent = option.label;
      select.appendChild(element);
    });
    select.value = selectedValue;
  }

  function initialize() {
    const cardOptions = data.cards.map((card) => ({
      value: card.cardId,
      label: `${card.cardId.slice(0, 8)} (${card.recordCount})`,
    }));
    const types = Array.from(new Set(data.transactions.map((row) => row.processName).filter(Boolean))).sort();
    const typeOptions = [
      { value: "all", label: "All types" },
      ...types.map((type) => ({ value: type, label: type })),
    ];
    const dates = data.transactions.map((row) => row.usedAt).filter(Boolean).sort();

    const initialCardId = cardOptions[0]?.value || "";
    if (initialCardId) {
      state.cardId = initialCardId;
    }

    setOptions(elements.cardFilter, cardOptions, state.cardId);
    setOptions(elements.typeFilter, typeOptions, state.type);
    elements.fromDate.value = dates[0] || "";
    elements.toDate.value = dates[dates.length - 1] || "";
    state.from = elements.fromDate.value;
    state.to = elements.toDate.value;
    elements.lastUpdated.textContent = data.generatedAt ? `Updated ${data.generatedAt}` : "No data generated yet";

    elements.cardFilter.addEventListener("change", () => {
      state.cardId = elements.cardFilter.value;
      state.showAllTransactions = false;
      render();
    });
    elements.typeFilter.addEventListener("change", () => {
      state.type = elements.typeFilter.value;
      state.showAllTransactions = false;
      render();
    });
    elements.fromDate.addEventListener("change", () => {
      state.from = elements.fromDate.value;
      state.showAllTransactions = false;
      render();
    });
    elements.toDate.addEventListener("change", () => {
      state.to = elements.toDate.value;
      state.showAllTransactions = false;
      render();
    });
    elements.resetFilters.addEventListener("click", () => {
      state.cardId = cardOptions[0]?.value || "";
      state.type = "all";
      state.from = dates[0] || "";
      state.to = dates[dates.length - 1] || "";
      state.showAllTransactions = false;
      elements.cardFilter.value = state.cardId;
      elements.typeFilter.value = state.type;
      elements.fromDate.value = state.from;
      elements.toDate.value = state.to;
      render();
    });
    elements.toggleTransactions.addEventListener("click", () => {
      state.showAllTransactions = !state.showAllTransactions;
      render();
    });

    render();
  }

  function filteredTransactions() {
    return data.transactions.filter((row) => {
      if (state.cardId && row.cardId !== state.cardId) return false;
      if (state.type !== "all" && row.processName !== state.type) return false;
      if (state.from && row.usedAt && row.usedAt < state.from) return false;
      if (state.to && row.usedAt && row.usedAt > state.to) return false;
      return true;
    });
  }

  function render() {
    const rows = filteredTransactions();
    const totalExpense = rows.reduce((sum, row) => sum + Number(row.expenseYen || 0), 0);
    const latest = rows.find((row) => Number.isFinite(Number(row.balanceYen)));
    const stationCounts = countStations(rows);
    const topStation = stationCounts[0]?.label || "-";

    elements.totalExpense.textContent = formatYen(totalExpense);
    elements.latestBalance.textContent = latest ? formatYen(latest.balanceYen) : "-";
    elements.transactionCount.textContent = rows.length.toLocaleString("en-US");
    elements.topStation.textContent = topStation;
    elements.cardPreviewLabel.textContent = selectedCardLabel();
    elements.cardPreviewBalance.textContent = latest ? formatYen(latest.balanceYen) : "¥0";

    renderBars(elements.dailyChart, groupByDailySegments(rows), formatYen, "spend");
    renderBars(elements.typeChart, groupBy(rows, "processName", "expenseYen"), formatYen, "mix");
    renderBars(elements.stationChart, stationCounts.slice(0, 8), (value) => `${value}`, "station");
    renderScanStats();
    renderTable(rows);
  }

  function selectedCardLabel() {
    return state.cardId ? shortCard(state.cardId) : "Card";
  }

  function filteredScans() {
    return (data.scans || []).filter((scan) => !state.cardId || scan.cardId === state.cardId);
  }

  function groupBy(rows, labelKey, valueKey) {
    const totals = new Map();
    rows.forEach((row) => {
      const label = row[labelKey] || "Unknown";
      totals.set(label, (totals.get(label) || 0) + Number(row[valueKey] || 0));
    });
    return Array.from(totals, ([label, value]) => ({ label, value })).sort((a, b) => {
      if (labelKey === "usedAt") return a.label.localeCompare(b.label);
      return b.value - a.value || a.label.localeCompare(b.label);
    });
  }

  function groupByDailySegments(rows) {
    const totals = new Map();
    rows.forEach((row) => {
      const label = row.usedAt || "Unknown";
      if (!totals.has(label)) {
        totals.set(label, { label, value: 0, segments: new Map() });
      }
      const bucket = totals.get(label);
      const processName = row.processName || "Unknown";
      bucket.value += Number(row.expenseYen || 0);
      bucket.segments.set(processName, (bucket.segments.get(processName) || 0) + Number(row.expenseYen || 0));
    });

    return Array.from(totals.values())
      .map((item) => ({
        label: item.label,
        value: item.value,
        segments: Array.from(item.segments.entries())
          .map(([name, amount]) => ({ label: name, value: amount }))
          .sort((a, b) => b.value - a.value),
      }))
      .sort((a, b) => b.label.localeCompare(a.label));
  }

  function countStations(rows) {
    const totals = new Map();
    rows.forEach((row) => {
      [row.entryStation, row.exitStation].forEach((station) => {
        if (!station) return;
        totals.set(station, (totals.get(station) || 0) + 1);
      });
    });
    return Array.from(totals, ([label, value]) => ({ label, value })).sort(
      (a, b) => b.value - a.value || a.label.localeCompare(b.label),
    );
  }

  function renderBars(container, rows, valueFormatter, paletteName) {
    container.innerHTML = "";
    if (!rows.length) {
      container.innerHTML = '<div class="empty">No records in this range.</div>';
      return;
    }
    const maxValue = Math.max(...rows.map((row) => row.value), 1);
    rows.forEach((row, index) => {
      const intensity = row.value / maxValue;
      const bar = document.createElement("div");
      bar.className = "bar-row";

      if (row.segments && row.segments.length) {
        const total = row.value || 1;
        const segments = row.segments
          .map((segment) => ({
            ...segment,
            width: (Number(segment.value || 0) / total) * 100,
            color: segmentColor(segment.label, paletteName),
          }))
          .filter((segment) => segment.width > 0);

        bar.innerHTML = `
          <span class="bar-label" title="${escapeHtml(row.label)}">${escapeHtml(row.label)}</span>
          <span class="bar-track">
            ${segments
              .map(
                (segment) =>
                  `<span class="stacked-segment" style="width: ${segment.width}%; background: ${segment.color};"></span>`,
              )
              .join("")}
          </span>
          <span class="bar-value">${escapeHtml(valueFormatter(row.value))}</span>
        `;
      } else {
        bar.innerHTML = `
          <span class="bar-label" title="${escapeHtml(row.label)}">${escapeHtml(row.label)}</span>
          <span class="bar-track"><span class="bar-fill ${paletteName}" style="width: ${intensity * 100}%; background: ${barColor(row.label, paletteName, index, intensity)}"></span></span>
          <span class="bar-value">${escapeHtml(valueFormatter(row.value))}</span>
        `;
      }
      container.appendChild(bar);
    });
  }

  function renderTable(rows) {
    elements.transactionsTable.innerHTML = "";
    const visibleRows = state.showAllTransactions ? rows : rows.slice(0, 5);
    elements.tableSummary.textContent = `${rows.length.toLocaleString("en-US")} records`;
    elements.toggleTransactions.hidden = rows.length <= 5;
    elements.toggleTransactions.textContent = state.showAllTransactions ? "Show less" : `Show ${rows.length - 5} more`;
    if (!rows.length) {
      const row = document.createElement("tr");
      row.innerHTML = '<td colspan="5" class="empty">No transactions match the current filters.</td>';
      elements.transactionsTable.appendChild(row);
      return;
    }

    visibleRows.forEach((item) => {
      const row = document.createElement("tr");
      const changeClass = Number(item.balanceChangeYen || 0) < 0 ? "negative" : "positive";
      const route = item.route || "-";
      const jpRoute =
        item.entryStationJapanese && item.exitStationJapanese
          ? `${item.entryStationJapanese} to ${item.exitStationJapanese}`
          : "";
      row.innerHTML = `
        <td>${escapeHtml(item.usedAt || "-")}</td>
        <td>${escapeHtml(item.processName || "-")}</td>
        <td class="${changeClass}">${escapeHtml(formatSignedYen(item.balanceChangeYen))}</td>
        <td>${escapeHtml(formatYen(item.balanceYen))}</td>
        <td class="route">${escapeHtml(route)}${jpRoute ? `<small>${escapeHtml(jpRoute)}</small>` : ""}</td>
      `;
      elements.transactionsTable.appendChild(row);
    });
  }

  function renderScanStats() {
    const scans = filteredScans().slice().sort((a, b) => String(b.scannedAt || "").localeCompare(String(a.scannedAt || "")));
    elements.scanStats.innerHTML = "";
    elements.scanSummary.textContent = `${scans.length.toLocaleString("en-US")} scans`;
    if (!scans.length) {
      elements.scanStats.innerHTML = '<div class="empty">No scan history yet.</div>';
      return;
    }

    scans.slice(0, 6).forEach((scan) => {
      const item = document.createElement("div");
      item.className = "scan-item";
      item.innerHTML = `
        <strong>${escapeHtml(scan.scannedAt || "-")}</strong>
        <span>${escapeHtml(shortCard(scan.cardId))}</span>
        <span>${Number(scan.recordsRead || 0).toLocaleString("en-US")} read</span>
        <span>${Number(scan.newRecords || 0).toLocaleString("en-US")} new</span>
        <span>${Number(scan.duplicateRecords || 0).toLocaleString("en-US")} duplicates</span>
        <span>${Number(scan.totalRecords || 0).toLocaleString("en-US")} total</span>
      `;
      elements.scanStats.appendChild(item);
    });
  }

  function shortCard(cardId) {
    return cardId ? `${String(cardId).slice(0, 8)}` : "-";
  }

  function barColor(label, paletteName, index, intensity) {
    const opacity = 0.42 + intensity * 0.58;
    if (paletteName === "station") {
      return index % 2 === 0 ? `rgba(245, 139, 52, ${opacity})` : `rgba(255, 178, 91, ${opacity})`;
    }
    if (paletteName === "mix") {
      return segmentColor(label, paletteName).replace("0.9", `${opacity}`);
    }
    return index % 2 === 0 ? `rgba(99, 140, 255, ${opacity})` : `rgba(246, 128, 171, ${opacity})`;
  }

  function segmentColor(label, paletteName) {
    const normalized = String(label || "").toLowerCase();

    if (normalized.includes("fare") || normalized.includes("transport") || normalized.includes("card")) {
      return "rgba(95, 140, 255, 0.9)";
    }
    if (normalized.includes("retail") || normalized.includes("purchase") || normalized.includes("shop")) {
      return "rgba(72, 191, 166, 0.9)";
    }
    if (normalized.includes("bus")) {
      return "rgba(255, 185, 95, 0.9)";
    }
    if (normalized.includes("charge")) {
      return "rgba(122, 110, 247, 0.9)";
    }
    if (normalized.includes("unknown")) {
      return "rgba(148, 160, 184, 0.9)";
    }

    if (paletteName === "station") {
      return "rgba(245, 139, 52, 0.9)";
    }
    if (paletteName === "mix") {
      return "rgba(246, 128, 171, 0.9)";
    }
    return "rgba(99, 140, 255, 0.9)";
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  initialize();
})();
