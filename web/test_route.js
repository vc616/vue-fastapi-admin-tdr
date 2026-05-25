const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  const consoleLogs = [];
  page.on('console', msg => {
    consoleLogs.push(msg.text());
  });
  
  await page.goto('http://localhost:3100/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  
  await page.locator('input').nth(0).fill('admin');
  await page.locator('input').nth(1).fill('123456');
  await page.locator('button:has-text("登录")').click();
  await page.waitForTimeout(3000);
  
  // Filter addRoute logs
  const addRouteLogs = consoleLogs.filter(l => l.includes('[addRoute]'));
  console.log('=== addRoute Logs ===');
  addRouteLogs.forEach(l => console.log(l));
  
  await browser.close();
})();
