---
layout: page
title: Setup
permalink: /
---

<noscript>
  <div class="warn-banner">
    JavaScript is disabled. This page needs it to generate config files. Please enable JavaScript and reload.
  </div>
</noscript>

<div id="app" style="display:none">
  <div class="safety-banner">
    <strong>🔒 Everything happens in your browser.</strong>
    API keys are never sent anywhere — the generated files are downloaded
    directly to your machine. Never commit <code>.env</code> to git.
  </div>

  <form id="config-form" autocomplete="off">

    <!-- ── Small LLM ── -->
    <fieldset>
      <legend>🧠 Small LLM <span class="sub">— per-paper work (summarize, filter)</span></legend>
      <div class="role-grid">

        <label>
          Provider
          <select id="light-provider" data-role="light">
            <option value="anthropic">Anthropic</option>
            <option value="openai">OpenAI</option>
            <option value="deepseek">DeepSeek</option>
            <option value="groq">Groq</option>
            <option value="together">Together</option>
            <option value="ollama">Ollama</option>
            <option value="lm-studio">LM Studio</option>
            <option value="custom">Custom</option>
          </select>
        </label>

        <label>
          Model
          <input type="text" id="light-model" data-role="light" placeholder="claude-haiku-4-5">
        </label>

        <label class="base-url-label" id="light-base-url-label">
          Base URL
          <input type="text" id="light-base-url" data-role="light" placeholder="https://api.deepseek.com/v1">
        </label>

        <label>
          API key
          <input type="password" id="light-key" data-role="light" placeholder="sk-...">
        </label>

        <label>
          Env variable name
          <input type="text" id="light-env" data-role="light" value="ANTHROPIC_API_KEY">
        </label>

      </div>
    </fieldset>

    <!-- ── Large LLM ── -->
    <fieldset>
      <legend>🧠 Large LLM <span class="sub">— brief generation (top-N only)</span></legend>
      <div class="role-grid">

        <label>
          Provider
          <select id="heavy-provider" data-role="heavy">
            <option value="anthropic">Anthropic</option>
            <option value="openai">OpenAI</option>
            <option value="deepseek">DeepSeek</option>
            <option value="groq">Groq</option>
            <option value="together">Together</option>
            <option value="ollama">Ollama</option>
            <option value="lm-studio">LM Studio</option>
            <option value="custom">Custom</option>
          </select>
        </label>

        <label>
          Model
          <input type="text" id="heavy-model" data-role="heavy" placeholder="claude-opus-4-8">
        </label>

        <label class="base-url-label" id="heavy-base-url-label">
          Base URL
          <input type="text" id="heavy-base-url" data-role="heavy" placeholder="https://api.deepseek.com/v1">
        </label>

        <label>
          API key
          <input type="password" id="heavy-key" data-role="heavy" placeholder="sk-...">
        </label>

        <label>
          Env variable name
          <input type="text" id="heavy-env" data-role="heavy" value="ANTHROPIC_API_KEY">
        </label>

      </div>
    </fieldset>

    <!-- ── Topics ── -->
    <fieldset>
      <legend>📋 Topics</legend>
      <p class="hint">One per line. Be specific — "quantum computing" lets everything through.</p>
      <textarea id="topics" rows="6" placeholder="silicon spin qubits and exchange gates
charge noise and decoherence in quantum dots
cryogenic control of quantum processors"></textarea>

      <label class="bib-upload">
        <span>Optionally upload a <code>.bib</code> file to extract keyword suggestions:</span>
        <input type="file" id="bib-file" accept=".bib">
      </label>
      <div id="keyword-chips" class="chip-list"></div>
    </fieldset>

    <!-- ── Scout settings ── -->
    <fieldset>
      <legend>🔭 Scout</legend>
      <div class="role-grid scout-grid">
        <label>
          arXiv categories
          <input type="text" id="categories" value="cond-mat.mes-hall, quant-ph" placeholder="cond-mat.mes-hall, quant-ph">
        </label>
        <label>
          Lookback (days)
          <input type="number" id="lookback" value="1" min="1" max="7">
        </label>
        <label>
          Max results
          <input type="number" id="max-results" value="200" min="10" max="1000">
        </label>
      </div>
    </fieldset>

    <!-- ── Ranking ── -->
    <fieldset>
      <legend>⚖️ Ranking weights</legend>
      <div class="role-grid weight-grid">
        <label>
          LLM
          <input type="number" id="w-llm" value="0.6" min="0" max="1" step="0.1">
        </label>
        <label>
          Centrality
          <input type="number" id="w-centrality" value="0.3" min="0" max="1" step="0.1">
        </label>
        <label>
          Scites
          <input type="number" id="w-scites" value="0.1" min="0" max="1" step="0.1">
        </label>
        <label>
          Top N
          <input type="number" id="top-n" value="5" min="1" max="20">
        </label>
      </div>
    </fieldset>

    <div class="button-bar">
      <button type="button" id="download-yaml">⬇ Download sqout.yaml</button>
      <button type="button" id="download-env">⬇ Download .env</button>
      <button type="button" id="run-sqout">🚀 Download & Run</button>
    </div>

    <div id="run-status" class="run-status" style="display:none">
      <p>
        <strong>Move the downloaded <code>sqout-run.sh</code> into your sqout checkout
        directory</strong>, then:
      </p>
      <pre><code>chmod +x sqout-run.sh && ./sqout-run.sh</code></pre>
      <p class="hint">
        The script auto-activates <code>.venv</code> if it exists and writes
        <code>config/sqout.yaml</code> + <code>.env</code> before running
        <code>sqout run</code>.
      </p>
    </div>

  </form>
</div>

<script src="{{ '/assets/main.js' | relative_url }}"></script>
<link rel="stylesheet" href="{{ '/assets/style.css' | relative_url }}">