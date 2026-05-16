#!/usr/bin/env python3
"""
CLI 入口：本地运行测试
用法:
  python scripts/run_tests.py                    # 运行全部 api 测试
  python scripts/run_tests.py --module api       # 指定模块
  python scripts/run_tests.py --case test_login  # 指定用例文件
  python scripts/run_tests.py --allure           # 生成 Allure 报告
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="测试平台 CLI 入口")
    parser.add_argument("--module", default="api", choices=["api", "ui", "perf"], help="测试模块")
    parser.add_argument("--case", default="", help="具体测试文件或用例名")
    parser.add_argument("--env", default="dev", help="测试环境")
    parser.add_argument("--allure", action="store_true", help="生成 Allure 报告")
    parser.add_argument("-k", default="", help="pytest -k 过滤表达式")
    args = parser.parse_args()

    os.environ["TEST_ENV"] = args.env
    os.environ["PYTHONPATH"] = str(ROOT)

    cmd = ["pytest", "-v", "--tb=short"]

    if args.case:
        target = ROOT / args.module / args.case
        if not target.exists():
            target = ROOT / args.module / f"{args.case}.py"
    else:
        target = ROOT / args.module

    cmd.append(str(target))

    if args.k:
        cmd.extend(["-k", args.k])

    if args.allure:
        cmd.append(f"--alluredir={ROOT}/reports/allure-results")

    print(f"[test-engine] 运行: {' '.join(cmd)}")
    sys.exit(subprocess.run(cmd, cwd=str(ROOT)).returncode)


if __name__ == "__main__":
    main()
