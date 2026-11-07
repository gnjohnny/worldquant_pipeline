# WorldQuant BRAIN Simulator Companion (Browser HUD)

The **Browser Simulator Companion** is a zero-cost, zero-dependency, client-side assistant designed to eliminate manual data entry, dropdown clicking, and backtest copy-pasting on WorldQuant BRAIN (`platform.worldquantbrain.com/simulate`).

---

## 1. Why It Is 100% Terms of Service (ToS) Compliant

- **No Scraping or Bots**: It does **not** scrape private API endpoints, automate logins, or execute unauthorized network requests.
- **Human-in-the-Loop**: You still log in normally and manually click the "Simulate" button.
- **Client-Side Ergonomics**: It operates strictly inside your active browser tab to bridge clipboard data with the simulator's code editor and results view (analogous to a password manager or Grammarly).

---

## 2. Key Capabilities

1. **Clipboard Batch Ingestion**:
   - Copy any batch from our chat (e.g. Batch 245) or a batch JSON file.
   - Click **`📋 Load Batch from Clipboard`**.
   - The companion parses all 3 candidates, showing their IDs and statuses in a neat queue.
2. **Ergonomic Draggable HUD & Auto-Settings**:
   - **Non-Intrusive Default**: Placed at **Bottom-Right** (or wherever you prefer) so it never blocks the simulator's **Settings** gear or header navigation.
   - **Draggable Anywhere**: Click and hold the header `⋮⋮ Move` bar to drag it anywhere across your browser window. Position is saved automatically.
   - **1-Click Docking (`⤢ Dock`)**: Cycle between screen corners (Bottom-Right, Bottom-Left, Top-Left, Mid-Right).
   - **Minimize to Floating Pill (`−`)**: Collapses to a compact 195px floating bar when reviewing charts.
   - **Auto-Opens Settings**: Automatically detects and expands the platform's Settings drawer if Decay/Delay fields are hidden.
   - **Monaco Injection & `📋 Copy Expr`**: Multi-strategy Monaco editor updater with a dedicated copy button.
3. **One-Click Result Harvesting**:
   - Once the simulation backtest completes on BRAIN, click **`📊 Harvest Result`**.
   - Extracts the pass/fail checks, Sharpe, Fitness, Turnover, and Sub-universe metrics cleanly from the screen.
   - Advances to the next candidate in the queue automatically.
4. **Full Batch Stacking**:
   - After testing all 3 candidates, click **`📥 Copy Full Batch Results`**.
   - Your clipboard now contains the unified 3-candidate results block ready to paste directly into our chat or the pipeline CLI!

---

## 3. Quick 10-Second Setup

Choose any of the three installation methods below:

### Method A: Browser Bookmarklet (Recommended - Simplest)
1. In Chrome / Edge / Brave, press `Ctrl + Shift + O` to open Bookmarks Manager.
2. Click **Add new bookmark**.
3. Name it: **`WQ Companion`**.
4. In the **URL** field, paste the contents of [`tools/companion/bookmarklet.txt`](bookmarklet.txt).
5. Save. Whenever you are on `platform.worldquantbrain.com`, simply click the bookmark to launch the HUD!

### Method B: Tampermonkey / Violentmonkey Userscript (Runs Automatically)
1. Install the [Tampermonkey](https://www.tampermonkey.net/) or [Violentmonkey](https://violentmonkey.github.io/) extension.
2. Create a new script and paste the entire contents of [`tools/companion/brain_companion.js`](brain_companion.js).
3. Save. The HUD will now appear automatically whenever you open the BRAIN simulator.

### Method C: Chrome DevTools Console / Snippet
1. On `platform.worldquantbrain.com`, press `F12` to open DevTools.
2. Go to the **Console** tab (or **Sources -> Snippets**).
3. Paste the contents of [`brain_companion.js`](brain_companion.js) and press `Enter`.

---

## 4. End-to-End Workflow Walkthrough

```
[ Antigravity Chat / CLI ]
       │  (1) Copy Candidate Batch Cards
       ▼
[ BRAIN Simulator Tab ]
       │  (2) Click "Load Batch from Clipboard"
       │  (3) Click "Apply Candidate 1" -> Click "Simulate"
       │  (4) When finished, Click "Harvest Result"
       │  (5) Repeat for Candidate 2 & 3
       │  (6) Click "Copy Full Batch Results"
       ▼
[ Antigravity Chat / CLI ]
          (7) Paste Full Block -> Auto-recorded into PostgreSQL!
```
