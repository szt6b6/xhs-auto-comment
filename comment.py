"""
评论功能模块 - 支持人类行为模拟
"""

from utils import (
    random_delay, parse_template, is_detected,
    HumanTyping, HumanMouse, HumanBehavior, get_random_template
)
import config


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


class CommentBot:
    def __init__(self, page):
        self.page = page
        self.success_count = 0
        self.fail_count = 0
        self.human = HumanBehavior(page)

    def comment_with_selectors(self, activate_selector, input_selector, submit_selector, template, post_info):
        """使用指定选择器评论（带人类行为模拟）"""
        try:
            activate_xpath = parse_xpath(activate_selector)
            input_xpath = parse_xpath(input_selector)
            submit_xpath = parse_xpath(submit_selector)

            # 获取模板（随机选择）
            message = get_random_template()

            # 检查是否跳过
            if self.human.should_skip_comment():
                print("  [跳过] 随机决定不评论此帖")
                return False

            # 1. 点击激活评论框（带鼠标轨迹和悬停）
            activate_el = self.page.wait_for_selector(f"xpath={activate_xpath}", timeout=5000)

            # 可能先悬停
            HumanMouse.maybe_hover(self.page, activate_el)

            # 鼠标移动到元素（自然曲线）
            self.human.random_mouse_move_to_element(activate_el)

            # 点击（带位置偏移）
            dx, dy = HumanMouse.random_click_offset()
            box = activate_el.bounding_box()
            click_x = box['x'] + box['width'] / 2 + dx
            click_y = box['y'] + box['height'] / 2 + dy
            self.page.mouse.click(click_x, click_y)

            print("  已点击激活评论框")
            random_delay(500, 1000)

            # 2. 等待输入框出现
            input_el = self.page.wait_for_selector(f"xpath={input_xpath}", timeout=5000)

            # 3. 人类打字（带速度波动和退格纠正）
            human_typist = HumanTyping(self.page, input_el)
            human_typist.type_with_human_behavior(message)

            random_delay(300, 800)

            # 4. 点击发送（带鼠标轨迹）
            submit_el = self.page.query_selector(f"xpath={submit_xpath}")
            if submit_el:
                self.human.random_mouse_move_to_element(submit_el)

                dx, dy = HumanMouse.random_click_offset()
                box = submit_el.bounding_box()
                click_x = box['x'] + box['width'] / 2 + dx
                click_y = box['y'] + box['height'] / 2 + dy
                self.page.mouse.click(click_x, click_y)

                print(f"  评论发送成功: {message[:20]}...")
                self.success_count += 1
                return True

        except Exception as e:
            print(f"  评论失败: {e}")
            self.fail_count += 1

        return False

    def comment_with_random_template(self, activate_selector, input_selector, submit_selector, post_info):
        """使用随机模板评论"""
        template = get_random_template()
        return self.comment_with_selectors(
            activate_selector, input_selector, submit_selector,
            template, post_info
        )

    def get_stats(self):
        return {"success": self.success_count, "fail": self.fail_count}