"""
帖子采集模块 - 支持间歇性浏览模式

采集搜索结果页面的帖子链接
"""

import random
import time
from utils import HumanScroll, HumanBrowse, HumanBehavior

BASE_URL = "https://www.xiaohongshu.com"


def parse_xpath(selector):
    """解析 xpath 选择器，返回 Playwright 格式的 xpath 表达式"""
    if selector.startswith("xpath://"):
        return selector[6:]
    elif selector.startswith("//"):
        return selector
    elif selector.startswith("xpath:"):
        return selector[6:]
    else:
        return selector


class PostCollector:
    """帖子采集器 - 支持间歇性浏览模式"""

    def __init__(self, page):
        self.page = page
        self.posts = []
        self.human = HumanBehavior(page)

    def collect_with_human_browse(self, container_selector, post_selector, min_posts=5, max_posts=20):
        """
        间歇性浏览采集模式 - 模拟人类边浏览边采集

        Args:
            container_selector: 容器选择器
            post_selector: 帖子卡片选择器
            min_posts: 最少采集数量
            max_posts: 最多采集数量

        Returns:
            帖子链接列表
        """
        posts = []
        scroll_count = 0
        last_new_post_count = 0
        no_new_count = 0

        print(f"开始间歇性浏览采集 (目标: {min_posts}-{max_posts} 个帖子)...")

        while len(posts) < max_posts and no_new_count < 5:
            # 人类滚动行为
            self.human.human_scroll_and_stay()

            # 采集当前可见的帖子
            new_posts = self._collect_visible_posts(container_selector, post_selector, posts)

            if new_posts:
                posts.extend(new_posts)
                no_new_count = 0
                print(f"  已采集 {len(posts)} 个帖子 (本次新增 {len(new_posts)} 个)")
            else:
                no_new_count += 1

            # 随机决定是否进入详情页"看看"
            if random.random() < 0.15 and posts:
                self._maybe_browse_post_detail(posts[-1])

            # 达到最低数量且还有新帖子时，可以继续采集
            if len(posts) >= min_posts and no_new_count >= 2:
                break

            scroll_count += 1

        print(f"采集完成，共 {len(posts)} 个帖子")
        self.posts = posts
        return posts

    def _collect_visible_posts(self, container_selector, post_selector, existing_posts):
        """采集当前可见的帖子"""
        posts = []
        try:
            container_xpath = parse_xpath(container_selector)
            post_xpath = parse_xpath(post_selector)

            self.page.wait_for_selector(f"xpath={container_xpath}", timeout=5000)
            cards = self.page.query_selector_all(f"xpath={post_xpath}")

            for card in cards:
                link_el = card.query_selector('a.cover.mask.ld')
                if not link_el:
                    link_el = card.query_selector('a[href*="/discovery/item"]')

                if link_el:
                    href = link_el.get_attribute("href")
                    if href:
                        if not href.startswith('http'):
                            href = BASE_URL + href
                        if href not in existing_posts and href not in posts:
                            posts.append(href)

        except Exception as e:
            print(f"采集出错: {e}")

        return posts

    def _maybe_browse_post_detail(self, post_url):
        """可能浏览帖子详情（模拟人类行为）"""
        try:
            print(f"  随机浏览详情页...")
            self.page.goto(post_url, wait_until="domcontentloaded")
            browse_time = random.uniform(3, 8)
            time.sleep(browse_time)

            # 随机滚动一下模拟浏览
            HumanScroll.random_scroll(self.page)
            time.sleep(random.uniform(2, 5))

            # 返回
            self.page.go_back()
            time.sleep(random.uniform(1, 3))
        except Exception:
            pass

    def collect(self, container_selector, post_selector):
        """兼容旧接口的采集方法（快速采集，不模拟人类）"""
        return self._collect_visible_posts(container_selector, post_selector, [])

    def get_posts(self):
        return self.posts

    def clear(self):
        self.posts = []