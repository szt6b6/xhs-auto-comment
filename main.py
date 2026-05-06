"""
小红书自动评论 - Playwright 自动化
主入口 - 支持反检测增强

用法:
    python main.py --keyword "关键词"                    # 搜索关键词
    python main.py --keyword "关键词" --scroll 10        # 指定滚动次数
    python main.py --keyword "关键词" --min-posts 5      # 最少采集帖子数
    python main.py --keyword "关键词" --max-posts 20     # 最多采集帖子数
"""

import sys
import argparse
import random
import time
from browser import BrowserManager
from collector import PostCollector
from comment import CommentBot
from utils import random_delay, HumanBehavior, get_random_template, is_detected
from utils import HumanScroll, HumanBrowse
import config


def print_banner():
    print("=" * 50)
    print("  小红书自动评论助手 (Playwright)")
    print("  [反检测增强版]")
    print("=" * 50)


def run_batch_comment(browser_mgr, keyword, min_posts, max_posts):
    """批量评论模式 - 间歇性浏览"""
    page = browser_mgr.page
    collector = PostCollector(page)
    comment_bot = CommentBot(page)
    human = HumanBehavior(page)

    # 访问搜索页
    search_url = f"{config.BASE_URL}/search_result?keyword={keyword}&type=51"
    print(f"\n访问搜索页: {keyword}")
    page.goto(search_url, wait_until="domcontentloaded")

    # 进入主页后先自然浏览一段时间（模拟人类）
    print(f"主页浏览中 ({config.HOME_PAGE_STAY_MIN}-{config.HOME_PAGE_STAY_MAX}秒)...")
    HumanBrowse.stay_on_page(page, config.HOME_PAGE_STAY_MIN, config.HOME_PAGE_STAY_MAX)

    # 间歇性浏览采集
    posts = collector.collect_with_human_browse(
        config.CONTAINER_SELECTOR,
        config.POST_SELECTOR,
        min_posts=min_posts,
        max_posts=max_posts
    )

    if not posts:
        print("\n未采集到帖子，请检查选择器是否正确")
        return

    print(f"\n共采集到 {len(posts)} 个帖子，开始评论...")

    # 遍历评论
    success_count = 0
    fail_count = 0

    for i, post_url in enumerate(posts):
        if post_url.startswith('/'):
            post_url = config.BASE_URL + post_url

        print(f"\n[{i+1}/{len(posts)}] 访问: {post_url[:60]}...")

        try:
            page.goto(post_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 检查是否被风控
            if is_detected(page):
                print("  [警告] 检测到风控，暂停等待...")
                time.sleep(config.CAPTCHA_WAIT_TIME)

            # 评论（使用随机模板）
            result = comment_bot.comment_with_random_template(
                config.COMMENT_ACTIVATE,
                config.COMMENT_INPUT,
                config.COMMENT_SUBMIT,
                {"title": "帖子", "author": "作者", "location": ""}
            )

            if result:
                print("  ✓ 成功")
                success_count += 1
            else:
                print("  ✗ 失败或跳过")
                fail_count += 1

        except Exception as e:
            print(f"  处理出错: {e}")
            fail_count += 1

        # 随机延迟（可能带长延迟模拟休息）
        human.random_delay_with_long_break()

        # 返回搜索页继续
        try:
            page.goto(search_url, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)

            # 随机滚动一下模拟自然返回
            if random.random() < 0.3:
                HumanScroll.random_scroll(page)

        except Exception:
            pass

    print(f"\n完成! 成功: {success_count}, 失败/跳过: {fail_count}")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description='小红书自动评论 [反检测增强版]')
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--min-posts', type=int, default=5, help='最少采集帖子数 (默认5)')
    parser.add_argument('--max-posts', type=int, default=20, help='最多采集帖子数 (默认20)')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    parser.add_argument('--no-login', action='store_true', help='跳过登录检查')

    args = parser.parse_args()

    # 启动浏览器
    browser_mgr = BrowserManager()
    config.BROWSER_HEADLESS = args.headless

    print("启动浏览器...")
    browser_mgr.start(load_cookies=True)
    print("浏览器已启动")

    # 检查登录状态
    if not args.no_login:
        if not browser_mgr.check_login_status():
            print("未检测到登录状态，请手动扫码登录...")
            print("请在浏览器窗口中扫码登录...")
            # 等待登录成功（轮询检查）
            while not browser_mgr.check_login_status():
                import time
                time.sleep(2)
            print("检测到登录成功!")
            # 登录成功后立即保存cookies
            browser_mgr.save_cookies("cookies.json")
            print("Cookies已保存，自动开始执行...")
        else:
            print("已通过Cookies恢复登录状态")

    # 执行批量评论
    print(f"\n关键词: {args.keyword}")
    print(f"采集目标: {args.min_posts}-{args.max_posts} 个帖子")

    run_batch_comment(browser_mgr, args.keyword, args.min_posts, args.max_posts)

    # 保存cookies
    browser_mgr.save_cookies("cookies.json")

    # 关闭
    input("\n按回车键关闭浏览器...")
    browser_mgr.close()
    print("再见!")


if __name__ == "__main__":
    main()