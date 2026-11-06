/* Ecrã de entrada de conveniência para GitHub Pages.
   IMPORTANTE: não é autenticação de servidor, os ficheiros continuam públicos. */
(() => {
  'use strict';
  const KEY = 'amf_estudio_access_session';
  const FINGERPRINT = '21694999947ce99bd5c90e9bcb2734e23f87f86d0b381f57fe3b0185da57edd3';
  const form = document.getElementById('access-form');
  const input = document.getElementById('access-pin');
  const error = document.getElementById('access-error');
  const button = document.getElementById('access-submit');

  async function verify(pin) {
    if (!window.crypto || !crypto.subtle) throw new Error('A verificação requer ligação segura (HTTPS).');
    const bytes = new TextEncoder().encode(pin);
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    const fingerprint = [...new Uint8Array(digest)].map(n => n.toString(16).padStart(2, '0')).join('');
    return fingerprint === FINGERPRINT;
  }

  function loadScript(source) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      // O preview público executa o HTML noutro domínio: usar assets JS com MIME correto.
      const isPreview = location.hostname === 'htmlpreview.github.io' || location.hostname === 'html-preview.github.io';
      const prefix = isPreview ? 'https://cdn.jsdelivr.net/gh/Xtvback/central@main/editorial/' : '';
      script.src = prefix + source;
      script.onload = resolve;
      script.onerror = () => reject(new Error('Não foi possível carregar ' + source));
      document.body.appendChild(script);
    });
  }

  async function enter() {
    button.disabled = true;
    error.textContent = 'A abrir o teu estúdio…';
    try {
      await loadScript('data.js');
      await loadScript('app.js');
      document.body.classList.add('unlocked');
      document.getElementById('access-screen').hidden = true;
      const actions = document.querySelector('.top-actions');
      if (actions) {
        const lock = document.createElement('button');
        lock.type = 'button';
        lock.className = 'lock-button';
        lock.textContent = 'Sair';
        lock.title = 'Bloquear o painel neste navegador';
        lock.addEventListener('click', () => {
          sessionStorage.removeItem(KEY);
          location.reload();
        });
        actions.appendChild(lock);
      }
    } catch (err) {
      sessionStorage.removeItem(KEY);
      button.disabled = false;
      error.textContent = 'Não foi possível abrir o painel. Atualiza a página e tenta novamente.';
    }
  }

  if (sessionStorage.getItem(KEY) === 'ok') {
    enter();
  } else {
    input.focus();
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (button.disabled) return;
    const code = input.value.trim();
    if (!/^\d{4}$/.test(code)) {
      error.textContent = 'Introduz os quatro algarismos do código.';
      input.focus();
      return;
    }
    button.disabled = true;
    error.textContent = 'A verificar…';
    try {
      if (await verify(code)) {
        sessionStorage.setItem(KEY, 'ok');
        await enter();
      } else {
        error.textContent = 'Código incorreto. Tenta novamente.';
        input.value = '';
        input.focus();
      }
    } catch (err) {
      error.textContent = 'Não foi possível validar o código neste navegador.';
    } finally {
      if (!document.body.classList.contains('unlocked')) button.disabled = false;
    }
  });
})();