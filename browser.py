"""
浏览器管理模块
"""

from playwright.sync_api import sync_playwright
import config


# 反检测 JavaScript 代码
ANTI_DETECT_JS = """
(function() {
    // 1. 移除 webdriver 属性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true
    });

    // 2. Canvas 指纹噪声注入
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, attributes) {
        const context = originalGetContext.call(this, type, attributes);
        if (type === '2d') {
            const originalFillText = context.fillText;
            const noiseRange = %d;
            context.fillText = function(...args) {
                // 添加微小噪声，不影响可读性
                if (Math.random() < 0.3) {
                    const noise = (Math.random() - 0.5) * noiseRange;
                    args[1] = args[1] !== undefined ? args[1] + noise : undefined;
                    args[2] = args[2] !== undefined ? args[2] + noise : undefined;
                }
                return originalFillText.apply(this, args);
            };
        }
        return context;
    };

    // 3. WebGL 参数随机化
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {
        // 随机化某些参数
        if (p === 37445) { // UNMASKED_VENDOR
            const vendors = ['Intel Inc.', 'NVIDIA Corporation', 'AMD', 'Apple'];
            return vendors[Math.floor(Math.random() * vendors.length)];
        }
        if (p === 37446) { // UNMASKED_RENDERER
            const renderers = ['Intel Iris OpenGL Engine', 'NVIDIA GeForce GTX 1060', 'AMD Radeon Pro 5500M', 'Apple M1'];
            return renderers[Math.floor(Math.random() * renderers.length)];
        }
        return getParameter.call(this, p);
    };

    // 4. Navigator 属性随机化
    const originalHardwareConcurrency = Object.getOwnPropertyDescriptor(Navigator.prototype, 'hardwareConcurrency');
    if (originalHardwareConcurrency && originalHardwareConcurrency.get) {
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => %d,
            configurable: true
        });
    }

    const originalDeviceMemory = Object.getOwnPropertyDescriptor(Navigator.prototype, 'deviceMemory');
    if (originalDeviceMemory && originalDeviceMemory.get) {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => %d,
            configurable: true
        });
    }

    // 5. 屏蔽自动化检测特征
    window.navigator.chrome = { runtime: {} };

    // 6. 覆盖 plugins 属性
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3],
        configurable: true
    });

    // 7. 模拟真实的 permissions API
    const originalPermissions = navigator.permissions;
    if (originalPermissions) {
        Object.defineProperty(navigator, 'permissions', {
            value: {
                query: (perm) => Promise.resolve({ state: 'prompt', add: originalPermissions.query ? originalPermissions.query.bind(navigator.permissions) : null })
            },
            configurable: true
        });
    }

    console.log('[Anti-Detect] Browser fingerprint protection activated');
})();
"""


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self, load_cookies=True):
        """启动浏览器"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=config.BROWSER_HEADLESS,
            slow_mo=config.BROWSER_SLOW_MO,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
            ]
        )
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=config.FAKE_UA_LIST[0] if config.FAKE_UA_LIST else None
        )

        # 尝试加载cookies
        if load_cookies:
            self.load_cookies("cookies.json")

        self.page = self.context.new_page()

        # 注入反检测脚本
        self.inject_anti_detect()

        return self.page

    def inject_anti_detect(self):
        """注入反检测脚本"""
        import random

        # 从配置中获取参数
        noise = random.randint(config.CANVAS_NOISE_MIN, config.CANVAS_NOISE_MAX)
        if noise == 0:
            noise = 1  # 避免除零

        hardware_concurrency = random.randint(config.HARDWARE_CONCURRENCY_MIN, config.HARDWARE_CONCURRENCY_MAX)
        device_memory = random.randint(config.DEVICE_MEMORY_MIN, config.DEVICE_MEMORY_MAX)

        js_code = ANTI_DETECT_JS % (noise, hardware_concurrency, device_memory)
        self.page.evaluate(js_code)

    def check_login_status(self):
        """检查是否已登录"""
        try:
            self.page.goto(config.BASE_URL, wait_until="networkidle", timeout=10000)
            self.page.wait_for_timeout(2000)

            login_popup = self.page.query_selector('.login-modal, .login-wrapper, [class*="login-popup"]')
            if login_popup:
                return False
            return True
        except Exception:
            return False

    def new_page(self):
        """创建新页面"""
        new_page = self.context.new_page()
        # 为新页面也注入反检测脚本
        self.inject_anti_detect_to_page(new_page)
        return new_page

    def inject_anti_detect_to_page(self, page):
        """为指定页面注入反检测脚本"""
        import random

        noise = random.randint(config.CANVAS_NOISE_MIN, config.CANVAS_NOISE_MAX)
        if noise == 0:
            noise = 1

        hardware_concurrency = random.randint(config.HARDWARE_CONCURRENCY_MIN, config.HARDWARE_CONCURRENCY_MAX)
        device_memory = random.randint(config.DEVICE_MEMORY_MIN, config.DEVICE_MEMORY_MAX)

        js_code = ANTI_DETECT_JS % (noise, hardware_concurrency, device_memory)
        page.evaluate(js_code)

    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def save_cookies(self, path="cookies.json"):
        """保存cookies"""
        cookies = self.context.cookies()
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
        print(f"Cookies已保存到 {path}")

    def load_cookies(self, path="cookies.json"):
        """加载cookies"""
        import json
        import os
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)

            # 确保 cookie 格式正确，补充必要的字段
            for cookie in cookies:
                # 小红书需要正确的 domain 设置
                if 'domain' not in cookie or not cookie['domain']:
                    cookie['domain'] = '.xiaohongshu.com'
                # 确保 SameSite 属性
                if 'sameSite' not in cookie:
                    cookie['sameSite'] = 'Lax'

            self.context.add_cookies(cookies)
            print(f"Cookies已从 {path} 加载 (共 {len(cookies)} 条)")
            return True
        return False