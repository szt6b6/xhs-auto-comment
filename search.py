"""
搜索功能模块
"""

from playwright.sync_api import sync_playwright
import config


class SearchEngine:
    def __init__(self, page):
        self.page = page

    def go_to_search(self, keyword):
        """跳转到搜索页面"""
        url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
        self.page.goto(url, wait_until="networkidle")
        self.page.wait_for_timeout(2000)  # 等待页面稳定
        print(f"已跳转到搜索页: {keyword}")

    def scroll_to_load_more(self, times=5):
        """滚动加载更多内容"""
        for i in range(times):
            self.page.evaluate("window.scrollBy(0, 800)")
            self.page.wait_for_timeout(1000)
            print(f"滚动第 {i+1}/{times} 次")

    def get_current_url(self):
        """获取当前URL"""
        return self.page.url