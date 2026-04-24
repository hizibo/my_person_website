# Pytest 接口自动化测试框架搭建

> 来源：综合整理自 CSDN、知乎等技术文章  
> 整理日期：2026-04-25

---

## 一、技术选型

| 组件 | 用途 | 安装命令 |
|------|------|----------|
| **pytest** | 测试框架核心 | `pip install pytest` |
| **requests** | HTTP 请求库 | `pip install requests` |
| **allure-pytest** | 测试报告生成 | `pip install allure-pytest` |
| **pytest-xdist** | 并行测试执行 | `pip install pytest-xdist` |
| **PyYAML** | YAML 配置文件解析 | `pip install pyyaml` |

---

## 二、项目结构

```
project/
├── common/              # 公共方法层
│   ├── __init__.py
│   ├── http_utils.py    # HTTP 请求封装
│   ├── read_yaml.py     # YAML 文件读取
│   └── logger.py        # 日志配置
├── config/              # 配置文件层
│   ├── config.ini       # 环境配置
│   └── config.yaml      # 测试数据配置
├── testcase/            # 测试用例层
│   ├── __init__.py
│   ├── conftest.py      # pytest  fixtures
│   └── test_login.py    # 具体测试用例
├── data/                # 测试数据层
│   └── login_data.yaml  # 测试数据文件
├── logs/                # 日志文件
├── report/              # 测试报告
├── temp/                # allure 临时文件
├── pytest.ini           # pytest 配置文件
└── main.py              # 主入口
```

---

## 三、核心代码实现

### 1. HTTP 请求封装 (common/http_utils.py)

```python
import requests
import logging

logger = logging.getLogger(__name__)

class HttpUtils:
    """HTTP 请求工具类"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, url, params=None, headers=None, **kwargs):
        """GET 请求"""
        full_url = f"{self.base_url}{url}"
        logger.info(f"GET 请求: {full_url}")
        response = self.session.get(full_url, params=params, headers=headers, **kwargs)
        logger.info(f"响应: {response.status_code} - {response.text[:200]}")
        return response
    
    def post(self, url, data=None, json=None, headers=None, **kwargs):
        """POST 请求"""
        full_url = f"{self.base_url}{url}"
        logger.info(f"POST 请求: {full_url}")
        response = self.session.post(full_url, data=data, json=json, headers=headers, **kwargs)
        logger.info(f"响应: {response.status_code} - {response.text[:200]}")
        return response
    
    def put(self, url, data=None, **kwargs):
        """PUT 请求"""
        full_url = f"{self.base_url}{url}"
        return self.session.put(full_url, data=data, **kwargs)
    
    def delete(self, url, **kwargs):
        """DELETE 请求"""
        full_url = f"{self.base_url}{url}"
        return self.session.delete(full_url, **kwargs)
```

### 2. YAML 数据读取 (common/read_yaml.py)

```python
import yaml
import os

class ReadYaml:
    """读取 YAML 文件"""
    
    @staticmethod
    def read_yaml_file(file_path):
        """读取 YAML 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def get_test_data(data_file, case_name):
        """获取测试用例数据"""
        data_path = os.path.join(os.path.dirname(__file__), '../data', data_file)
        data = ReadYaml.read_yaml_file(data_path)
        return data.get('testcases', {}).get(case_name, [])
```

### 3. conftest.py 配置

```python
import pytest
import os
from common.http_utils import HttpUtils
from common.read_yaml import ReadYaml

@pytest.fixture(scope="session")
def base_url():
    """基础 URL"""
    return "http://localhost:8080"

@pytest.fixture(scope="session")
def http_client(base_url):
    """HTTP 客户端"""
    return HttpUtils(base_url)

@pytest.fixture(scope="function")
def common_params():
    """公共参数"""
    return {
        "Content-Type": "application/json;charset=UTF-8"
    }
```

### 4. 测试用例示例 (testcase/test_login.py)

```python
import pytest
import allure
from common.read_yaml import ReadYaml

@allure.feature("用户登录模块")
class TestLogin:
    
    @allure.story("正常登录")
    @allure.title("验证用户输入正确用户名和密码能成功登录")
    @pytest.mark.parametrize("test_data", ReadYaml.get_test_data('login_data.yaml', 'test_login'))
    def test_login_success(self, http_client, common_params, test_data):
        """测试正常登录"""
        method, url, headers, data, expected = test_data
        
        # 发送请求
        response = http_client.post(url, json=data, headers={**common_params, **headers})
        
        # 断言
        assert response.status_code == 200
        result = response.json()
        assert result['code'] == expected
        assert 'token' in result['data']
    
    @allure.story("异常登录")
    @allure.title("验证错误密码登录失败")
    @pytest.mark.parametrize("test_data", [
        ("POST", "/api/login", {"username": "test", "password": "wrong"}, 401)
    ])
    def test_login_fail(self, http_client, common_params, test_data):
        """测试错误密码登录"""
        method, url, data, expected = test_data
        
        response = http_client.post(url, json=data, headers=common_params)
        result = response.json()
        
        assert result['code'] == expected
```

### 5. 测试数据文件 (data/login_data.yaml)

```yaml
testcases:
  test_login:
    - ["POST", "/api/login", {"Content-Type": "application/json"}, {"username": "admin", "password": "123456"}, 200]
    - ["POST", "/api/login", {"Content-Type": "application/json"}, {"username": "user1", "password": "password"}, 200]
```

### 6. pytest.ini 配置

```ini
[pytest]
testpaths = testcase
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --alluredir=temp --clean-alluredir
markers =
    smoke: 冒烟测试
    regression: 回归测试
```

---

## 四、运行测试

### 1. 执行所有测试
```bash
pytest
```

### 2. 生成 Allure 报告
```bash
pytest --alluredir=temp
allure generate temp -o report --clean
allure open report
```

### 3. 并行执行
```bash
pytest -n auto  # 根据 CPU 核心数自动分配
```

### 4. 按标记执行
```bash
pytest -m smoke      # 只执行冒烟测试
pytest -m "not slow" # 排除慢用例
```

---

## 五、核心特性说明

### 1. Fixture 依赖注入
pytest 的 fixture 机制可以实现：
- 测试数据准备和清理
- 数据库连接管理
- 接口认证 token 获取

### 2. 参数化测试
使用 `@pytest.mark.parametrize` 可以实现：
- 同一用例多组数据测试
- 数据驱动测试
- 减少代码重复

### 3. Allure 报告
- `@allure.feature` - 功能模块
- `@allure.story` - 用户故事
- `@allure.title` - 用例标题
- `@allure.step` - 测试步骤
- `@allure.attach` - 附加信息

---

## 六、参考链接

- [构建强大的接口自动化测试框架 - CSDN](https://blog.csdn.net/chengxuyuznguoke/article/details/144562844)
- [pytest 之接口自动化实践 - CSDN](https://blog.csdn.net/qq_44663072/article/details/116137744)
- [测试开发实战项目 - 知乎](https://zhuanlan.zhihu.com/p/554542386)
