// ==UserScript==
// @name         WorldQuant BRAIN Simulator Companion
// @namespace    worldquant_pipeline
// @version      1.2.0
// @description  Zero-Cost Client-Side Assistant for WorldQuant BRAIN simulation workflow. Draggable HUD, auto-fills Monaco/Ace editor expressions, sets React parameters, and harvests backtest results for PostgreSQL pipeline.
// @author       worldquant_pipeline
// @match        https://platform.worldquantbrain.com/*
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  // Remove existing HUD if re-running bookmarklet
  const existingHud = document.getElementById('wq-companion-hud');
  if (existingHud) {
    existingHud.remove();
    console.log('[WQ Companion] Replaced existing HUD with fresh instance.');
  }

  // State Management
  const state = {
    batchData: [],
    currentIndex: 0,
    results: {}, // { candidateId: text }
  };

  // Toast Notification (Centered at top of screen)
  function showToast(msg, type = 'success') {
    let toast = document.getElementById('wq-companion-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'wq-companion-toast';
      Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        padding: '10px 20px',
        borderRadius: '8px',
        color: '#fff',
        fontSize: '13px',
        fontWeight: '600',
        zIndex: '100000',
        boxShadow: '0 6px 20px rgba(0,0,0,0.5)',
        transition: 'opacity 0.3s ease, transform 0.3s ease',
        fontFamily: 'Inter, system-ui, sans-serif',
        pointerEvents: 'none'
      });
      document.body.appendChild(toast);
    }
    toast.style.background = type === 'error' ? '#ef4444' : type === 'info' ? '#3b82f6' : '#10b981';
    toast.innerText = msg;
    toast.style.opacity = '1';
    toast.style.transform = 'translateX(-50%) translateY(0)';
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(-50%) translateY(-10px)';
    }, 3200);
  }

  // React Input Helper: Trigger React onChange
  function setReactInputValue(inputEl, value) {
    if (!inputEl) return;
    try {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
      if (nativeSetter) {
        nativeSetter.call(inputEl, value);
      } else {
        inputEl.value = value;
      }
      inputEl.dispatchEvent(new Event('input', { bubbles: true }));
      inputEl.dispatchEvent(new Event('change', { bubbles: true }));
    } catch (e) {
      console.warn('[WQ Companion] Failed setting input via React setter:', e);
      inputEl.value = value;
    }
  }

  // Multi-Strategy Editor Value Injection (Monaco / Ace / Native ExecCommand)
  function setEditorValue(code) {
    let injected = false;

    // Strategy 1: Check window.monaco API (Standard global)
    if (window.monaco && window.monaco.editor) {
      try {
        const editors = window.monaco.editor.getEditors();
        if (editors && editors.length > 0) {
          editors[0].setValue(code);
          console.log('[WQ Companion] Injected via window.monaco.editor.getEditors()');
          return true;
        }
        const models = window.monaco.editor.getModels();
        if (models && models.length > 0) {
          models[0].setValue(code);
          console.log('[WQ Companion] Injected via window.monaco.editor.getModels()');
          return true;
        }
      } catch (e) {
        console.warn('[WQ Companion] window.monaco injection attempt failed:', e);
      }
    }

    // Strategy 2: Check window.ace API
    const aceEditorEl = document.querySelector('.ace_editor');
    if (aceEditorEl && window.ace) {
      try {
        const editor = window.ace.edit(aceEditorEl);
        editor.setValue(code, -1);
        console.log('[WQ Companion] Injected via window.ace.edit()');
        return true;
      } catch (e) {
        console.warn('[WQ Companion] window.ace injection attempt failed:', e);
      }
    }

    // Strategy 3: Inspect Monaco DOM container directly for attached editor instance
    const monacoContainers = document.querySelectorAll('.monaco-editor');
    for (const container of monacoContainers) {
      // Often frameworks store instance in container or properties
      for (const prop of Object.keys(container)) {
        if (prop.startsWith('__') && container[prop] && typeof container[prop].setValue === 'function') {
          container[prop].setValue(code);
          console.log('[WQ Companion] Injected via container property:', prop);
          return true;
        }
      }
    }

    // Strategy 4: Native Focus + execCommand('insertText') on the active Monaco/Ace input area
    // Monaco uses a hidden textarea with class 'inputarea' or within '.monaco-editor'
    const editorInputArea = document.querySelector('.monaco-editor textarea, .ace_editor textarea, textarea.inputarea, [role="code"] textarea');
    if (editorInputArea) {
      try {
        editorInputArea.focus();
        // Select all existing code
        document.execCommand('selectAll', false, null);
        // Replace with new code via insertText (Monaco intercepts this natively)
        const success = document.execCommand('insertText', false, code);
        if (success) {
          console.log('[WQ Companion] Injected via document.execCommand(insertText) on editor textarea.');
          return true;
        }
      } catch (e) {
        console.warn('[WQ Companion] execCommand insertion failed:', e);
      }
    }

    // Strategy 5: Direct React Fiber Property Traversal
    for (const container of monacoContainers) {
      const fiberKey = Object.keys(container).find(k => k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
      if (fiberKey) {
        let curr = container[fiberKey];
        while (curr) {
          if (curr.memoizedProps && typeof curr.memoizedProps.onChange === 'function') {
            try {
              curr.memoizedProps.onChange(code);
              console.log('[WQ Companion] Dispatched code update via React Fiber onChange.');
              return true;
            } catch (_) {}
          }
          if (curr.stateNode && typeof curr.stateNode.setValue === 'function') {
            try {
              curr.stateNode.setValue(code);
              console.log('[WQ Companion] Dispatched code update via React Fiber stateNode.setValue.');
              return true;
            } catch (_) {}
          }
          curr = curr.return;
        }
      }
    }

    // Strategy 6 (Guaranteed Fallback): Copy to clipboard & focus editor so Ctrl+V works instantly
    if (navigator.clipboard) {
      navigator.clipboard.writeText(code).then(() => {
        showToast('Code copied to clipboard! Click into editor and press Ctrl+V', 'info');
      });
      if (editorInputArea) editorInputArea.focus();
    }

    return false;
  }

  // Set Simulation Parameters in BRAIN React UI
  function applySimulatorSettings(settings = {}) {
    const universe = settings.universe || 'TOP3000';
    const neutralization = settings.neutralization || 'MARKET';
    const decay = settings.decay !== undefined ? settings.decay.toString() : '0';
    const delay = settings.delay !== undefined ? settings.delay.toString() : '1';
    const truncation = settings.truncation !== undefined ? settings.truncation.toString() : '0.01';

    console.log(`[WQ Companion] Applying Settings: Universe=${universe}, Neutralization=${neutralization}, Decay=${decay}, Delay=${delay}`);

    // Check if settings drawer / panel is closed and needs expanding
    const allButtons = Array.from(document.querySelectorAll('button, [role="button"]'));
    for (const b of allButtons) {
      const bText = (b.textContent || '').trim().toUpperCase();
      const aria = (b.getAttribute('aria-label') || '').toUpperCase();
      if ((bText === 'SETTINGS' || bText.includes('SIMULATION SETTING') || aria.includes('SETTING')) && !bText.includes('RESET')) {
        const hasInputs = Array.from(document.querySelectorAll('input')).some(i => {
          const pt = (i.closest('label, div, section')?.textContent || '').toLowerCase();
          return pt.includes('decay') || pt.includes('delay');
        });
        if (!hasInputs) {
          b.click();
          console.log('[WQ Companion] Auto-opened Settings drawer/panel.');
        }
        break;
      }
    }

    // 1. Text / Number Inputs for Decay, Delay, Truncation
    const allInputs = Array.from(document.querySelectorAll('input'));
    for (const input of allInputs) {
      const parentText = (input.closest('label, div, section')?.textContent || '').toLowerCase();
      const name = (input.name || input.id || input.placeholder || '').toLowerCase();

      if (parentText.includes('decay') || name.includes('decay')) {
        setReactInputValue(input, decay);
      } else if (parentText.includes('delay') || name.includes('delay')) {
        setReactInputValue(input, delay);
      } else if (parentText.includes('truncation') || name.includes('truncation')) {
        setReactInputValue(input, truncation);
      }
    }

    // 2. Custom Select Dropdowns for Universe and Neutralization
    // Click dropdown button if not already set, then select matching option
    const buttons = Array.from(document.querySelectorAll('button, [role="combobox"], [role="button"], .ant-select, .select-trigger'));
    
    // Helper to find and click an option in open dropdowns
    function selectDropdownOption(targetText) {
      setTimeout(() => {
        const options = Array.from(document.querySelectorAll('[role="option"], .ant-select-item-option-content, .dropdown-item, li'));
        const matched = options.find(o => o.textContent.trim().toUpperCase() === targetText.toUpperCase());
        if (matched) {
          matched.click();
          console.log(`[WQ Companion] Selected option: ${targetText}`);
        }
      }, 100);
    }

    for (const btn of buttons) {
      const btnText = btn.textContent.trim().toUpperCase();
      // If button is for Neutralization and doesn't match target
      if (btnText.includes('NEUTRALIZATION') || btnText === 'SUBINDUSTRY' || btnText === 'MARKET' || btnText === 'INDUSTRY') {
        if (!btnText.includes(neutralization.toUpperCase())) {
          btn.click();
          selectDropdownOption(neutralization);
        }
      }
      // If button is for Universe
      if (btnText.includes('UNIVERSE') || btnText === 'TOP3000' || btnText === 'TOP1000' || btnText === 'TOPSP500') {
        if (!btnText.includes(universe.toUpperCase())) {
          btn.click();
          selectDropdownOption(universe);
        }
      }
    }
  }

  // Harvest Backtest Results from Screen
  function harvestSimulationResults() {
    const allDivs = Array.from(document.querySelectorAll('div, section, article'));
    const matchedDivs = allDivs.filter(d => {
      const text = d.innerText || '';
      return (text.includes('PASS') || text.includes('FAIL')) && 
             (text.includes('Sharpe') || text.includes('Turnover') || text.includes('Fitness'));
    });

    if (matchedDivs.length > 0) {
      matchedDivs.sort((a, b) => a.innerText.length - b.innerText.length);
      return matchedDivs[0].innerText.trim();
    }

    const main = document.querySelector('main') || document.body;
    const lines = (main.innerText || '').split('\n').map(l => l.trim()).filter(Boolean);
    const relevant = lines.filter(l => 
      l.includes('PASS') || l.includes('FAIL') || 
      l.includes('Sharpe') || l.includes('Fitness') || 
      l.includes('Turnover') || l.includes('Sub-universe') || 
      l.includes('Self-correlation') || l.includes('Weight is') ||
      l.includes('Incompatible unit')
    );
    return relevant.join('\n');
  }

  // Parse clipboard input: JSON or markdown candidate cards
  function parseClipboardContent(text) {
    const candidates = [];

    // Attempt 1: Raw JSON
    try {
      const data = JSON.parse(text);
      if (data.hypotheses) {
        data.hypotheses.forEach((h, hIdx) => {
          (h.candidates || []).forEach((c, cIdx) => {
            candidates.push({
              id: c.id || `Hypo_${hIdx + 1}_Cand_${cIdx + 1}`,
              title: h.title || 'Untitled Candidate',
              expression: c.expression,
              decay: 0,
              neutralization: 'MARKET',
              universe: 'TOP3000'
            });
          });
        });
        if (candidates.length > 0) return candidates;
      }
    } catch (_) {}

    // Attempt 2: Markdown Candidate Cards
    const cardBlocks = text.split(/#### Candidate \d+:/i);
    if (cardBlocks.length > 1) {
      for (let i = 1; i < cardBlocks.length; i++) {
        const block = cardBlocks[i];
        const idMatch = block.match(/Candidate ID[:\*]*\s*`?([a-zA-Z0-9_-]+)`?/i);
        const exprMatch = block.match(/```(?:python)?\s*([\s\S]*?)```/i);
        const titleMatch = block.split('\n')[0].trim();

        if (exprMatch) {
          candidates.push({
            id: idMatch ? idMatch[1] : `Cand_${i}`,
            title: titleMatch || `Candidate ${i}`,
            expression: exprMatch[1].trim(),
            decay: 0,
            neutralization: 'MARKET',
            universe: 'TOP3000'
          });
        }
      }
      if (candidates.length > 0) return candidates;
    }

    // Attempt 3: Single code block or raw string
    const codeMatch = text.match(/```(?:python)?\s*([\s\S]*?)```/i);
    const expr = codeMatch ? codeMatch[1].trim() : text.trim();
    if (expr && expr.length > 10) {
      candidates.push({
        id: 'Candidate_1',
        title: 'Clipboard Candidate',
        expression: expr,
        decay: 0,
        neutralization: 'MARKET',
        universe: 'TOP3000'
      });
    }

    return candidates;
  }

  // Build HUD Interface
  function createHUD() {
    const hud = document.createElement('div');
    hud.id = 'wq-companion-hud';
    Object.assign(hud.style, {
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      width: '330px',
      backgroundColor: '#18181b',
      color: '#f4f4f5',
      borderRadius: '12px',
      border: '1px solid #3f3f46',
      boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
      zIndex: '99999',
      padding: '12px 14px',
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
      fontSize: '12px',
      userSelect: 'none',
      transition: 'box-shadow 0.2s ease, width 0.2s ease'
    });

    // Restore saved position if present
    try {
      const savedPos = JSON.parse(localStorage.getItem('wq_companion_pos') || 'null');
      if (savedPos && savedPos.left && savedPos.top) {
        hud.style.bottom = 'auto';
        hud.style.right = 'auto';
        hud.style.left = savedPos.left;
        hud.style.top = savedPos.top;
      }
    } catch (_) {}

    hud.innerHTML = `
      <div id="wq-hud-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; border-bottom:1px solid #27272a; padding-bottom:8px; cursor:grab; user-select:none;">
        <div style="display:flex; align-items:center; gap:6px;">
          <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10b981;"></span>
          <strong style="font-size:13px; color:#fafafa;">BRAIN Companion v1.2</strong>
          <span style="font-size:10px; color:#71717a;" title="Drag header to move anywhere">⋮⋮ Move</span>
        </div>
        <div style="display:flex; align-items:center; gap:4px;">
          <button id="wq-btn-dock" style="background:#27272a; border:1px solid #3f3f46; color:#a1a1aa; cursor:pointer; font-size:10px; padding:2px 6px; border-radius:4px;" title="Cycle screen corners">⤢ Dock</button>
          <button id="wq-btn-minimize" style="background:#27272a; border:1px solid #3f3f46; color:#a1a1aa; cursor:pointer; font-size:12px; padding:2px 6px; border-radius:4px;" title="Minimize to pill">−</button>
          <button id="wq-btn-close" style="background:#27272a; border:1px solid #3f3f46; color:#f87171; cursor:pointer; font-size:12px; padding:2px 6px; border-radius:4px;" title="Close Companion">✕</button>
        </div>
      </div>

      <div id="wq-hud-body">
        <div style="margin-bottom:10px;">
          <button id="wq-btn-load" style="width:100%; background:#2563eb; color:#fff; border:none; padding:8px 10px; border-radius:6px; cursor:pointer; font-weight:600; font-size:11px;">
            📋 Load Batch from Clipboard
          </button>
        </div>

        <div id="wq-queue-container" style="background:#09090b; border:1px solid #27272a; border-radius:8px; padding:8px; margin-bottom:10px; max-height:130px; overflow-y:auto;">
          <span style="color:#71717a; font-size:11px;">No candidates loaded. Copy batch in chat, then click "Load".</span>
        </div>

        <div style="display:flex; gap:6px; margin-bottom:10px;">
          <button id="wq-btn-fill" style="flex:2; background:#10b981; color:#fff; border:none; padding:9px 10px; border-radius:6px; cursor:pointer; font-weight:700; font-size:12px;">
            ⚡ Inject to Editor
          </button>
          <button id="wq-btn-copy-expr" style="flex:1; background:#3f3f46; color:#fff; border:none; padding:9px 6px; border-radius:6px; cursor:pointer; font-weight:600; font-size:11px;" title="Copy expression to clipboard for manual paste">
            📋 Copy Expr
          </button>
        </div>

        <div style="border-top:1px solid #27272a; padding-top:10px; display:flex; flex-direction:column; gap:6px;">
          <button id="wq-btn-harvest" style="background:#8b5cf6; color:#fff; border:none; padding:8px 10px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px;">
            📊 Harvest Current Backtest Result
          </button>
          <button id="wq-btn-copy-all" style="background:#27272a; color:#e4e4e7; border:1px solid #3f3f46; padding:7px 10px; border-radius:6px; cursor:pointer; font-weight:500; font-size:11px;">
            📥 Copy Full Batch Results (0/3 Recorded)
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(hud);

    // Draggable Logic
    let isDragging = false;
    let dragStartX = 0, dragStartY = 0, initialLeft = 0, initialTop = 0;
    const header = hud.querySelector('#wq-hud-header');

    header.addEventListener('mousedown', (e) => {
      if (e.target.tagName === 'BUTTON' || e.target.closest('button')) return;
      isDragging = true;
      header.style.cursor = 'grabbing';
      dragStartX = e.clientX;
      dragStartY = e.clientY;
      const rect = hud.getBoundingClientRect();
      initialLeft = rect.left;
      initialTop = rect.top;

      hud.style.bottom = 'auto';
      hud.style.right = 'auto';
      hud.style.left = `${initialLeft}px`;
      hud.style.top = `${initialTop}px`;
      e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const dx = e.clientX - dragStartX;
      const dy = e.clientY - dragStartY;

      const maxLeft = Math.max(10, window.innerWidth - hud.offsetWidth - 10);
      const maxTop = Math.max(10, window.innerHeight - hud.offsetHeight - 10);

      const newLeft = Math.max(10, Math.min(maxLeft, initialLeft + dx));
      const newTop = Math.max(10, Math.min(maxTop, initialTop + dy));

      hud.style.left = `${newLeft}px`;
      hud.style.top = `${newTop}px`;
    });

    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        header.style.cursor = 'grab';
        try {
          localStorage.setItem('wq_companion_pos', JSON.stringify({
            left: hud.style.left,
            top: hud.style.top
          }));
        } catch (_) {}
      }
    });

    // Cycle Corners: Bottom-Right -> Bottom-Left -> Top-Left -> Middle-Right
    const corners = [
      { name: 'Bottom-Right', bottom: '24px', right: '24px', left: 'auto', top: 'auto' },
      { name: 'Bottom-Left', bottom: '24px', left: '24px', right: 'auto', top: 'auto' },
      { name: 'Top-Left', top: '75px', left: '24px', right: 'auto', bottom: 'auto' },
      { name: 'Middle-Right', top: '220px', right: '24px', left: 'auto', bottom: 'auto' }
    ];
    let cornerIndex = 0;

    hud.querySelector('#wq-btn-dock').addEventListener('click', () => {
      cornerIndex = (cornerIndex + 1) % corners.length;
      const c = corners[cornerIndex];
      hud.style.bottom = c.bottom;
      hud.style.right = c.right;
      hud.style.left = c.left;
      hud.style.top = c.top;
      showToast(`Docked to ${c.name}`, 'info');
      try {
        localStorage.removeItem('wq_companion_pos');
      } catch (_) {}
    });

    // Minimize to pill
    let minimized = false;
    hud.querySelector('#wq-btn-minimize').addEventListener('click', () => {
      minimized = !minimized;
      const body = document.getElementById('wq-hud-body');
      const dragNote = hud.querySelector('#wq-hud-header span[title]');
      if (minimized) {
        body.style.display = 'none';
        hud.style.width = '195px';
        hud.querySelector('#wq-btn-minimize').innerText = '+';
        if (dragNote) dragNote.style.display = 'none';
      } else {
        body.style.display = 'block';
        hud.style.width = '330px';
        hud.querySelector('#wq-btn-minimize').innerText = '−';
        if (dragNote) dragNote.style.display = 'inline';
      }
    });

    // Close HUD
    hud.querySelector('#wq-btn-close').addEventListener('click', () => {
      hud.remove();
      showToast('Companion closed. Click bookmarklet to reopen anytime.', 'info');
    });

    // Load from Clipboard
    hud.querySelector('#wq-btn-load').addEventListener('click', async () => {
      try {
        const text = await navigator.clipboard.readText();
        const candidates = parseClipboardContent(text);
        if (candidates.length === 0) {
          showToast('No candidates found on clipboard. Copy batch cards first!', 'error');
          return;
        }
        state.batchData = candidates;
        state.currentIndex = 0;
        state.results = {};
        renderQueue();
        showToast(`Loaded ${candidates.length} candidates!`);
      } catch (e) {
        showToast('Clipboard access denied. Please allow clipboard permissions.', 'error');
      }
    });

    // Inject to Editor
    hud.querySelector('#wq-btn-fill').addEventListener('click', () => {
      if (state.batchData.length === 0) {
        showToast('Load a batch first!', 'error');
        return;
      }
      const cand = state.batchData[state.currentIndex];
      const success = setEditorValue(cand.expression);
      applySimulatorSettings(cand);

      if (success) {
        showToast(`Injected ${cand.id} into editor! Ready to Simulate.`);
      } else {
        showToast(`${cand.id} copied to clipboard! Click editor & press Ctrl+V`, 'info');
      }
    });

    // Copy Expression manually
    hud.querySelector('#wq-btn-copy-expr').addEventListener('click', () => {
      if (state.batchData.length === 0) {
        showToast('No candidate loaded!', 'error');
        return;
      }
      const cand = state.batchData[state.currentIndex];
      navigator.clipboard.writeText(cand.expression).then(() => {
        showToast(`Copied ${cand.id} expression! Press Ctrl+V in editor.`);
      });
    });

    // Harvest Result
    hud.querySelector('#wq-btn-harvest').addEventListener('click', () => {
      const activeCand = state.batchData[state.currentIndex] || { id: `Candidate_${state.currentIndex + 1}` };
      const rawText = harvestSimulationResults();
      if (!rawText || (!rawText.includes('PASS') && !rawText.includes('FAIL'))) {
        showToast('No completed backtest results found on screen. Wait for simulation!', 'error');
        return;
      }

      state.results[activeCand.id] = rawText;
      updateHarvestButtons();
      navigator.clipboard.writeText(`Candidate ${state.currentIndex + 1}:\n${rawText}`).then(() => {
        showToast(`Harvested ${activeCand.id} result!`);
      });

      if (state.currentIndex + 1 < state.batchData.length) {
        state.currentIndex++;
        renderQueue();
      }
    });

    // Copy Full Batch Results
    hud.querySelector('#wq-btn-copy-all').addEventListener('click', () => {
      const entries = Object.entries(state.results);
      if (entries.length === 0) {
        showToast('No results recorded yet.', 'error');
        return;
      }

      let fullText = '';
      state.batchData.forEach((c, idx) => {
        if (state.results[c.id]) {
          fullText += `Candidate ${idx + 1}:\n${state.results[c.id]}\n\n`;
        }
      });

      navigator.clipboard.writeText(fullText.trim()).then(() => {
        showToast(`Copied full batch (${entries.length}/${state.batchData.length})! Paste into chat.`);
      });
    });

    function renderQueue() {
      const q = document.getElementById('wq-queue-container');
      q.innerHTML = '';
      state.batchData.forEach((c, idx) => {
        const item = document.createElement('div');
        const isCurrent = idx === state.currentIndex;
        const hasResult = !!state.results[c.id];

        Object.assign(item.style, {
          padding: '6px 8px',
          marginBottom: '4px',
          borderRadius: '5px',
          cursor: 'pointer',
          background: isCurrent ? '#1e293b' : '#141416',
          border: isCurrent ? '1px solid #3b82f6' : '1px solid #27272a',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '11px',
          color: isCurrent ? '#60a5fa' : '#d4d4d8'
        });

        item.innerHTML = `
          <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:210px;">
            <strong>#${idx + 1}</strong>: ${c.id} (${c.title.slice(0, 18)}...)
          </span>
          <span>${hasResult ? '✅' : isCurrent ? '👉' : '⏳'}</span>
        `;

        item.addEventListener('click', () => {
          state.currentIndex = idx;
          renderQueue();
        });

        q.appendChild(item);
      });
      updateHarvestButtons();
    }

    function updateHarvestButtons() {
      const btnAll = document.getElementById('wq-btn-copy-all');
      const recorded = Object.keys(state.results).length;
      const total = state.batchData.length || 3;
      btnAll.innerText = `📥 Copy Full Batch Results (${recorded}/${total} Recorded)`;
      if (recorded === total && total > 0) {
        btnAll.style.background = '#10b981';
        btnAll.style.color = '#fff';
      }
    }
  }

  // Inject once DOM is interactive
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createHUD);
  } else {
    createHUD();
  }
})();
