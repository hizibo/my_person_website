"""
批量数据生成服务
支持 MySQL / Oracle SQL 脚本生成，Faker 随机数据，变量引用实现多表关联
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import random
import string
import re
from datetime import datetime, timedelta
from faker import Faker

app = FastAPI(title="批量数据生成服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_cn = Faker('zh_CN')

# ========== Faker 类型映射 ==========

FAKER_TYPES = {
    'name': {'label': '姓名', 'fn': lambda: fake_cn.name()},
    'first_name': {'label': '名', 'fn': lambda: fake_cn.first_name()},
    'last_name': {'label': '姓', 'fn': lambda: fake_cn.last_name()},
    'phone': {'label': '手机号', 'fn': lambda: fake_cn.phone_number()},
    'email': {'label': '邮箱', 'fn': lambda: fake_cn.email()},
    'province': {'label': '省份', 'fn': lambda: fake_cn.province()},
    'city': {'label': '城市', 'fn': lambda: fake_cn.city()},
    'district': {'label': '区县', 'fn': lambda: fake_cn.district()},
    'address': {'label': '详细地址', 'fn': lambda: fake_cn.address()},
    'company': {'label': '公司名', 'fn': lambda: fake_cn.company()},
    'job': {'label': '职位', 'fn': lambda: fake_cn.job()},
    'id_card': {'label': '身份证号', 'fn': lambda: fake_cn.ssn()},
    'credit_card': {'label': '信用卡号', 'fn': lambda: fake_cn.credit_card_number()},
    'postcode': {'label': '邮编', 'fn': lambda: fake_cn.postcode()},
    'country': {'label': '国家', 'fn': lambda: fake_cn.country()},
    'url': {'label': 'URL', 'fn': lambda: fake_cn.url()},
    'ip': {'label': 'IP地址', 'fn': lambda: fake_cn.ipv4()},
    'mac': {'label': 'MAC地址', 'fn': lambda: fake_cn.mac_address()},
    'uuid': {'label': 'UUID', 'fn': lambda: str(fake_cn.uuid4())},
    'isbn': {'label': 'ISBN', 'fn': lambda: fake_cn.isbn13()},
    'currency': {'label': '货币代码', 'fn': lambda: fake_cn.currency_code()},
    'username': {'label': '用户名', 'fn': lambda: fake_cn.user_name()},
    'password': {'label': '密码', 'fn': lambda: fake_cn.password()},
    'color': {'label': '颜色值', 'fn': lambda: fake_cn.hex_color()},
    'word': {'label': '单词', 'fn': lambda: fake_cn.word()},
    'sentence': {'label': '句子', 'fn': lambda: fake_cn.sentence()},
    'paragraph': {'label': '段落', 'fn': lambda: fake_cn.paragraph()},
    'boolean': {'label': '布尔值', 'fn': lambda: random.choice(['1', '0'])},
}


@app.get("/faker-types")
async def get_faker_types():
    """获取可用的 Faker 类型列表"""
    return {k: v['label'] for k, v in FAKER_TYPES.items()}


# ========== 数据模型 ==========

class RandomRule(BaseModel):
    type: str = "string"  # int, float, string, date, datetime, enum
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    decimal_places: Optional[int] = 2
    length: Optional[int] = 10
    charset: Optional[str] = "mixed"  # letters, digits, mixed, chinese
    prefix: Optional[str] = ""
    suffix: Optional[str] = ""
    start_date: Optional[str] = "2020-01-01"
    end_date: Optional[str] = "2026-12-31"
    date_format: Optional[str] = "%Y-%m-%d"
    enum_values: Optional[List[str]] = None


class FieldConfig(BaseModel):
    name: str
    data_type: str = "string"  # number, string, date, datetime
    fill_mode: str = "random"  # fixed, auto_increment, random, faker, variable
    fixed_value: Optional[str] = None
    start_value: Optional[int] = 1
    step: Optional[int] = 1
    random_rule: Optional[RandomRule] = None
    faker_type: Optional[str] = None
    variable_name: Optional[str] = None


class VariableConfig(BaseModel):
    name: str
    rule: RandomRule
    count: int = 100


class TableConfig(BaseModel):
    name: str
    row_count: int = 10
    fields: List[FieldConfig]


class GenerateRequest(BaseModel):
    database: str = "mysql"
    tables: List[TableConfig]
    variables: List[VariableConfig] = []


class GenerateResponse(BaseModel):
    sql: str
    message: str = "success"
    total_rows: int = 0


# ========== 数据生成逻辑 ==========

def generate_random_value(rule: RandomRule, row_index: int = 0) -> str:
    if rule.type == "int":
        min_v = int(rule.min_val or 0)
        max_v = int(rule.max_val or 100)
        return str(random.randint(min_v, max_v))

    elif rule.type == "float":
        min_v = rule.min_val or 0
        max_v = rule.max_val or 100
        dp = rule.decimal_places or 2
        val = random.uniform(min_v, max_v)
        return f"{val:.{dp}f}"

    elif rule.type == "string":
        length = rule.length or 10
        charset = rule.charset or "mixed"
        if charset == "digits":
            chars = string.digits
        elif charset == "letters":
            chars = string.ascii_letters
        elif charset == "chinese":
            raw = ''.join([chr(random.randint(0x4e00, 0x9fff)) for _ in range(length)])
            result = (rule.prefix or "") + raw + (rule.suffix or "")
            return result[:length + len(rule.prefix or "") + len(rule.suffix or "")]
        else:
            chars = string.ascii_letters + string.digits
        result = ''.join(random.choices(chars, k=length))
        return (rule.prefix or "") + result + (rule.suffix or "")

    elif rule.type == "date":
        start = datetime.strptime(rule.start_date or "2020-01-01", "%Y-%m-%d")
        end = datetime.strptime(rule.end_date or "2026-12-31", "%Y-%m-%d")
        delta = (end - start).days
        if delta <= 0:
            delta = 1
        result_date = start + timedelta(days=random.randint(0, delta))
        return result_date.strftime(rule.date_format or "%Y-%m-%d")

    elif rule.type == "datetime":
        start = datetime.strptime(rule.start_date or "2020-01-01", "%Y-%m-%d")
        end = datetime.strptime(rule.end_date or "2026-12-31", "%Y-%m-%d")
        delta = (end - start).total_seconds()
        if delta <= 0:
            delta = 86400
        result_date = start + timedelta(seconds=random.uniform(0, delta))
        return result_date.strftime("%Y-%m-%d %H:%M:%S")

    elif rule.type == "enum":
        values = rule.enum_values or ["选项1", "选项2", "选项3"]
        return random.choice(values)

    return "unknown"


def generate_field_value(field: FieldConfig, row_index: int, variable_values: Dict[str, List[str]]) -> str:
    if field.fill_mode == "fixed":
        return field.fixed_value or ""

    elif field.fill_mode == "auto_increment":
        start = field.start_value or 1
        step = field.step or 1
        return str(start + row_index * step)

    elif field.fill_mode == "random":
        if field.random_rule:
            return generate_random_value(field.random_rule, row_index)
        if field.data_type == "number":
            return str(random.randint(1, 1000))
        elif field.data_type == "date":
            return generate_random_value(RandomRule(type="date"), row_index)
        elif field.data_type == "datetime":
            return generate_random_value(RandomRule(type="datetime"), row_index)
        else:
            return generate_random_value(RandomRule(type="string"), row_index)

    elif field.fill_mode == "faker":
        faker_type = field.faker_type or "name"
        if faker_type in FAKER_TYPES:
            return FAKER_TYPES[faker_type]['fn']()
        return fake_cn.name()

    elif field.fill_mode == "variable":
        var_name = field.variable_name or ""
        if var_name in variable_values:
            values = variable_values[var_name]
            if row_index < len(values):
                return values[row_index]
            return values[row_index % len(values)]
        return ""

    return ""


def generate_variable_values(variables: List[VariableConfig]) -> Dict[str, List[str]]:
    result = {}
    for var in variables:
        values = []
        for i in range(var.count):
            values.append(generate_random_value(var.rule, i))
        result[var.name] = values
    return result


def escape_sql_value(value: str, data_type: str) -> str:
    if data_type == "number":
        try:
            float(value)
            return value
        except ValueError:
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def validate_identifier(name: str) -> bool:
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))


def generate_mysql_sql(request: GenerateRequest, variable_values: Dict[str, List[str]]) -> str:
    lines = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_rows = sum(t.row_count for t in request.tables)
    lines.append(f"-- ============================================")
    lines.append(f"-- 批量数据生成脚本 (MySQL)")
    lines.append(f"-- 生成时间: {now}")
    lines.append(f"-- 总表数: {len(request.tables)}, 总行数: {total_rows}")
    lines.append(f"-- ============================================")
    lines.append("")
    lines.append("START TRANSACTION;")
    lines.append("")

    for table in request.tables:
        lines.append(f"-- 表: {table.name} ({table.row_count} 条)")

        batch_size = 100
        for batch_start in range(0, table.row_count, batch_size):
            batch_end = min(batch_start + batch_size, table.row_count)
            value_rows = []
            for row_idx in range(batch_start, batch_end):
                values = []
                for field in table.fields:
                    val = generate_field_value(field, row_idx, variable_values)
                    values.append(escape_sql_value(val, field.data_type))
                value_rows.append(f"({', '.join(values)})")

            col_str = ", ".join(f.name for f in table.fields)
            lines.append(f"INSERT INTO {table.name} ({col_str}) VALUES")
            lines.append(",\n".join(f"  {row}" for row in value_rows) + ";")
            lines.append("")

    lines.append("COMMIT;")
    return "\n".join(lines)


def generate_oracle_sql(request: GenerateRequest, variable_values: Dict[str, List[str]]) -> str:
    lines = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_rows = sum(t.row_count for t in request.tables)
    lines.append(f"-- ============================================")
    lines.append(f"-- 批量数据生成脚本 (Oracle)")
    lines.append(f"-- 生成时间: {now}")
    lines.append(f"-- 总表数: {len(request.tables)}, 总行数: {total_rows}")
    lines.append(f"-- ============================================")
    lines.append("")

    for table in request.tables:
        lines.append(f"-- 表: {table.name} ({table.row_count} 条)")

        commit_batch = 500
        for row_idx in range(table.row_count):
            if row_idx % commit_batch == 0 and row_idx > 0:
                lines.append("COMMIT;")
                lines.append("")

            columns = []
            values = []
            for field in table.fields:
                columns.append(field.name)
                val = generate_field_value(field, row_idx, variable_values)
                values.append(escape_sql_value(val, field.data_type))

            col_str = ", ".join(columns)
            val_str = ", ".join(values)
            lines.append(f"INSERT INTO {table.name} ({col_str}) VALUES ({val_str});")

        lines.append("")

    lines.append("COMMIT;")
    return "\n".join(lines)


@app.post("/generate", response_model=GenerateResponse)
async def generate_sql(request: GenerateRequest):
    if not request.tables:
        raise HTTPException(status_code=400, detail="至少需要一张表")

    for table in request.tables:
        if not table.name.strip():
            raise HTTPException(status_code=400, detail="表名不能为空")
        if not validate_identifier(table.name):
            raise HTTPException(status_code=400, detail=f"表名 '{table.name}' 不合法，仅支持字母/数字/下划线")
        if not table.fields:
            raise HTTPException(status_code=400, detail=f"表 {table.name} 至少需要一个字段")
        for field in table.fields:
            if not field.name.strip():
                raise HTTPException(status_code=400, detail=f"表 {table.name} 有字段名为空")
            if not validate_identifier(field.name):
                raise HTTPException(status_code=400, detail=f"字段名 '{field.name}' 不合法，仅支持字母/数字/下划线")
        if table.row_count < 1 or table.row_count > 100000:
            raise HTTPException(status_code=400, detail=f"表 {table.name} 行数须在 1-100000 之间")

    # Auto-calc variable count
    variable_values = {}
    for var in request.variables:
        max_count = var.count
        for table in request.tables:
            for field in table.fields:
                if field.fill_mode == "variable" and field.variable_name == var.name:
                    max_count = max(max_count, table.row_count)
        var.count = max_count
        vals = []
        for i in range(var.count):
            vals.append(generate_random_value(var.rule, i))
        variable_values[var.name] = vals

    if request.database == "oracle":
        sql = generate_oracle_sql(request, variable_values)
    else:
        sql = generate_mysql_sql(request, variable_values)

    total_rows = sum(t.row_count for t in request.tables)

    return GenerateResponse(
        sql=sql,
        message=f"成功生成 {total_rows} 条数据",
        total_rows=total_rows
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "data-generator"}
