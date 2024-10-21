const puppeteer = require('puppeteer');

async function triggerXSS(UserName, PassWord) {
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        executablePath: '/usr/bin/chromium',
        headless: true
    });

    const page = await browser.newPage();

    await page.goto('http://localhost:3000/login');

    await page.type('input[name="username"]', UserName);
    await page.type('input[name="password"]', PassWord);

    await page.click('button[type="submit"]');

    await page.goto('http://localhost:3000/');

    await browser.close();

    return;
}

module.exports = { triggerXSS };
