# Selenium 自动化测试实战

> 来源：综合整理自 CSDN、脚本之家等技术文章  
> 整理日期：2026-04-25

---

## 一、环境搭建

### 1. 安装依赖

```bash
# 安装 Selenium
pip install selenium

# 安装 WebDriver（以 Chrome 为例）
# 1. 查看 Chrome 版本：chrome://version/
# 2. 下载对应版本的 ChromeDriver：https://chromedriver.chromium.org/
# 3. 将 chromedriver 放到系统 PATH 中
```

### 2. 验证环境

```python
from selenium import webdriver

# 启动浏览器
driver = webdriver.Chrome()
driver.get("https://www.baidu.com")
print(driver.title)
driver.quit()
```

---

## 二、元素定位方法

### 1. 八大定位方式

| 定位方式 | 方法 | 适用场景 |
|----------|------|----------|
| **ID** | `find_element(By.ID, "id")` | 元素有唯一 id |
| **Name** | `find_element(By.NAME, "name")` | 表单元素 |
| **Class Name** | `find_element(By.CLASS_NAME, "class")` | 样式类名 |
| **Tag Name** | `find_element(By.TAG_NAME, "tag")` | 标签名 |
| **Link Text** | `find_element(By.LINK_TEXT, "文本")` | 完整链接文本 |
| **Partial Link Text** | `find_element(By.PARTIAL_LINK_TEXT, "部分文本")` | 部分链接文本 |
| **CSS Selector** | `find_element(By.CSS_SELECTOR, "css")` | 灵活强大 |
| **XPath** | `find_element(By.XPATH, "xpath")` | 最灵活通用 |

### 2. 定位示例

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.baidu.com")

# ID 定位
search_box = driver.find_element(By.ID, "kw")

# Name 定位
search_box = driver.find_element(By.NAME, "wd")

# Class Name 定位
search_box = driver.find_element(By.CLASS_NAME, "s_ipt")

# CSS Selector 定位
search_box = driver.find_element(By.CSS_SELECTOR, "#kw")
search_box = driver.find_element(By.CSS_SELECTOR, "input[name='wd']")

# XPath 定位
search_box = driver.find_element(By.XPATH, "//input[@id='kw']")
search_box = driver.find_element(By.XPATH, "//input[@name='wd']")

# 定位多个元素
results = driver.find_elements(By.CSS_SELECTOR, ".result")
```

### 3. XPath 高级用法

```python
# 绝对路径（不推荐）
/driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/input")

# 相对路径
 driver.find_element(By.XPATH, "//input[@id='username']")

# 文本包含
driver.find_element(By.XPATH, "//*[contains(text(), '登录')]")

# 多属性组合
driver.find_element(By.XPATH, "//input[@type='text' and @name='username']")

# 父/子/兄弟节点
driver.find_element(By.XPATH, "//div[@class='parent']/input")
driver.find_element(By.XPATH, "//input[@id='a']/following-sibling::input")
driver.find_element(By.XPATH, "//input[@id='b']/preceding-sibling::input")

# 模糊匹配
driver.find_element(By.XPATH, "//*[starts-with(@id, 'user')]")
driver.find_element(By.XPATH, "//*[contains(@class, 'btn')]")
```

---

## 三、元素操作

### 1. 基本操作

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://example.com")

# 点击元素
button = driver.find_element(By.ID, "submit")
button.click()

# 输入文本
input_box = driver.find_element(By.ID, "username")
input_box.send_keys("test_user")

# 清空输入框
input_box.clear()

# 获取元素文本
text = driver.find_element(By.ID, "message").text

# 获取属性值
value = driver.find_element(By.ID, "input").get_attribute("value")
href = driver.find_element(By.LINK_TEXT, "链接").get_attribute("href")

# 获取元素大小和位置
size = element.size
location = element.location
```

### 2. 键盘和鼠标操作

```python
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 键盘操作
input_box.send_keys("Hello")
input_box.send_keys(Keys.ENTER)  # 回车
input_box.send_keys(Keys.TAB)    # Tab
input_box.send_keys(Keys.CONTROL + 'a')  # 全选
input_box.send_keys(Keys.CONTROL + 'c')  # 复制
input_box.send_keys(Keys.CONTROL + 'v')  # 粘贴

# 鼠标操作
actions = ActionChains(driver)

# 悬停
actions.move_to_element(element).perform()

# 右键点击
actions.context_click(element).perform()

# 双击
actions.double_click(element).perform()

# 拖拽
actions.drag_and_drop(source, target).perform()

# 拖拽到指定位置
actions.drag_and_drop_by_offset(source, xoffset=100, yoffset=0).perform()
```

---

## 四、等待机制

### 1. 隐式等待

```python
# 设置全局等待时间
driver.implicitly_wait(10)  # 10秒内等待元素出现
```

### 2. 显式等待（推荐）

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 等待元素可点击
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, "submit")))

# 常用等待条件
EC.presence_of_element_located((By.ID, "id"))      # 元素存在
EC.visibility_of_element_located((By.ID, "id"))    # 元素可见
EC.element_to_be_clickable((By.ID, "id"))          # 元素可点击
EC.text_to_be_present_in_element((By.ID, "id"), "text")  # 包含文本
EC.title_contains("Expected Title")                # 标题包含
EC.alert_is_present()                              # 弹窗出现
```

### 3. 自定义等待条件

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

def wait_for_element_text(driver, locator, expected_text, timeout=10):
    """等待元素文本变为期望值"""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(
            lambda d: d.find_element(*locator).text == expected_text
        )
    except TimeoutException:
        return False
```

---

## 五、特殊元素处理

### 1. iframe 切换

```python
# 切换到 iframe（通过索引）
driver.switch_to.frame(0)

# 切换到 iframe（通过 name 或 id）
driver.switch_to.frame("frame_name")

# 切换到 iframe（通过元素）
iframe = driver.find_element(By.TAG_NAME, "iframe")
driver.switch_to.frame(iframe)

# 切换到父级 frame
driver.switch_to.parent_frame()

# 切换到主文档
driver.switch_to.default_content()
```

### 2. 弹窗处理

```python
from selenium.webdriver.common.alert import Alert

# 切换到 alert
alert = driver.switch_to.alert

# 获取弹窗文本
text = alert.text

# 点击确定
alert.accept()

# 点击取消
alert.dismiss()

# 输入文本（prompt 弹窗）
alert.send_keys("input text")
```

### 3. 下拉框处理

```python
from selenium.webdriver.support.ui import Select

# 定位下拉框
select = Select(driver.find_element(By.ID, "select_id"))

# 通过可见文本选择
select.select_by_visible_text("选项文本")

# 通过 value 选择
select.select_by_value("option_value")

# 通过索引选择
select.select_by_index(0)

# 获取所有选项
options = select.options
for option in options:
    print(option.text)
```

### 4. 文件上传

```python
# 直接发送文件路径到 input 元素
upload_input = driver.find_element(By.ID, "file_input")
upload_input.send_keys("/path/to/file.txt")
```

### 5. 多窗口/标签页切换

```python
# 获取当前窗口句柄
main_window = driver.current_window_handle

# 获取所有窗口句柄
all_windows = driver.window_handles

# 切换到新窗口
for window in all_windows:
    if window != main_window:
        driver.switch_to.window(window)
        break

# 关闭当前窗口
driver.close()

# 切换回主窗口
driver.switch_to.window(main_window)
```

---

## 六、浏览器操作

```python
# 浏览器前进/后退/刷新
driver.back()
driver.forward()
driver.refresh()

# 设置窗口大小
driver.set_window_size(1920, 1080)
driver.maximize_window()
driver.minimize_window()

# 执行 JavaScript
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
driver.execute_script("arguments[0].scrollIntoView();", element)

# 获取 Cookie
cookies = driver.get_cookies()
driver.add_cookie({'name': 'key', 'value': 'value'})
driver.delete_cookie('key')
driver.delete_all_cookies()

# 截图
driver.save_screenshot("screenshot.png")
element.screenshot("element.png")
```

---

## 七、Page Object 模式

### 1. 基础 Page 类

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def find_element(self, *locator):
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def click(self, *locator):
        self.find_element(*locator).click()
    
    def send_keys(self, text, *locator):
        element = self.find_element(*locator)
        element.clear()
        element.send_keys(text)
```

### 2. 具体页面类

```python
class LoginPage(BasePage):
    # 定位器
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-msg")
    
    def login(self, username, password):
        self.send_keys(username, *self.USERNAME_INPUT)
        self.send_keys(password, *self.PASSWORD_INPUT)
        self.click(*self.LOGIN_BUTTON)
    
    def get_error_message(self):
        return self.find_element(*self.ERROR_MESSAGE).text
```

### 3. 测试用例

```python
import unittest
from selenium import webdriver
from pages.login_page import LoginPage

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://example.com/login")
        self.login_page = LoginPage(self.driver)
    
    def tearDown(self):
        self.driver.quit()
    
    def test_login_success(self):
        self.login_page.login("valid_user", "valid_pass")
        # 验证登录成功
        self.assertIn("首页", self.driver.title)
    
    def test_login_failure(self):
        self.login_page.login("invalid_user", "invalid_pass")
        error_msg = self.login_page.get_error_message()
        self.assertEqual(error_msg, "用户名或密码错误")

if __name__ == "__main__":
    unittest.main()
```

---

## 八、最佳实践

### 1. 异常处理

```python
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException
)

try:
    element = driver.find_element(By.ID, "id")
    element.click()
except NoSuchElementException:
    print("元素未找到")
except TimeoutException:
    print("等待超时")
except ElementNotInteractableException:
    print("元素不可交互")
```

### 2. 配置管理

```python
# config.py
class Config:
    BASE_URL = "https://example.com"
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 20
    
    # 浏览器配置
    BROWSER = "chrome"
    HEADLESS = False
    
    # 账号信息
    TEST_USER = "test_user"
    TEST_PASSWORD = "test_pass"
```

### 3. 测试数据分离

```python
# test_data.yaml
login:
  valid_user:
    username: "test_user"
    password: "test_pass"
  invalid_user:
    username: "wrong_user"
    password: "wrong_pass"
    expected_error: "用户名或密码错误"
```

---

## 九、常见问题

### Q1: 元素定位失败？
**A**: 
- 检查元素是否在 iframe 中
- 等待元素加载完成
- 检查元素是否被其他元素遮挡

### Q2: 页面加载超时？
**A**: 
- 使用显式等待代替 time.sleep()
- 检查网络连接
- 增加超时时间

### Q3: 浏览器驱动版本不匹配？
**A**: 
- 确保 ChromeDriver 版本与 Chrome 浏览器版本一致
- 使用 WebDriverManager 自动管理驱动

```python
# 使用 webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
```

---

## 十、参考链接

- [Selenium Python 自动化测试 - CSDN](https://blog.csdn.net/qq_46362865/article/details/159228206)
- [Python Selenium 自动化测试 - 脚本之家](https://www.jb51.net/article/213476.htm)
- [Selenium 官方文档](https://www.selenium.dev/documentation/)
