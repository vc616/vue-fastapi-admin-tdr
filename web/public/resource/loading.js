/**
 * 初始化加载效果的svg格式logo
 * @param {string} id - 元素id
 */
 function initSvgLogo(id) {
  const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0F172A;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1E293B;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#22C55E;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#4ADE80;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect x="15" y="20" width="70" height="60" rx="4" fill="url(#grad1)" stroke="currentColor" stroke-width="2"/>
  <rect x="22" y="32" width="25" height="18" rx="2" fill="url(#grad2)" opacity="0.8"/>
  <rect x="53" y="32" width="25" height="18" rx="2" fill="url(#grad2)" opacity="0.6"/>
  <rect x="22" y="55" width="56" height="3" rx="1" fill="url(#grad2)" opacity="0.4"/>
  <rect x="22" y="62" width="40" height="3" rx="1" fill="url(#grad2)" opacity="0.3"/>
  <circle cx="78" cy="22" r="12" fill="url(#grad1)" stroke="currentColor" stroke-width="2"/>
  <path d="M74 22 L77 25 L83 19" stroke="#22C55E" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`
  const appEl = document.querySelector(id)
  const div = document.createElement('div')
  div.innerHTML = svgStr
  if (appEl) {
    appEl.appendChild(div)
  }
}

function addThemeColorCssVars() {
  const key = '__THEME_COLOR__'
  const defaultColor = '#0F172A'
  const themeColor = window.localStorage.getItem(key) || defaultColor
  const cssVars = `--primary-color: ${themeColor}`
  document.documentElement.style.cssText = cssVars
}

addThemeColorCssVars()

initSvgLogo('#loadingLogo')
