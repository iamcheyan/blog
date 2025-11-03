#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pelican 博客自动构建和本地服务器
自动执行构建流程并在本地启动开发服务器
"""

import os
import sys
import argparse
import subprocess
import signal
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent.absolute()


def print_step(step, message):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step}: {message}")
    print(f"{'='*60}\n")


def check_virtualenv():
    """检查虚拟环境是否激活"""
    if not os.environ.get('VIRTUAL_ENV'):
        venv_path = BASE_DIR / 'venv'
        if venv_path.exists():
            print("⚠️  虚拟环境未激活，正在尝试激活...")
            print("   请手动运行: source venv/bin/activate")
            print("   或者运行: source venv/bin/activate && python app.py")
            return False
    return True


def run_command(cmd, check=True):
    """运行命令"""
    print(f"执行: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            check=check,
            cwd=BASE_DIR,
            capture_output=False
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ 命令未找到，请确保已安装 Pelican")
        return False


def build_site(config='pelicanconf.py'):
    """构建网站"""
    print_step(1, "构建 Pelican 网站")
    
    cmd = ['pelican', 'content', '-s', config]
    if not run_command(cmd):
        print("❌ 构建失败")
        return False
    
    print("✅ 构建完成")
    return True


def start_server(port=8000, autoreload=True):
    """启动本地服务器"""
    print_step(2, f"启动本地服务器 (端口: {port})")
    
    cmd = ['pelican', '--listen', '-p', str(port)]
    if autoreload:
        cmd.insert(1, '--autoreload')
        print("✅ 已启用自动重载模式（文件变化时自动重新构建）")
    
    print(f"\n🚀 服务器启动中...")
    print(f"   访问地址: http://127.0.0.1:{port}")
    print(f"   按 Ctrl+C 停止服务器\n")
    
    try:
        # 启动服务器（这会阻塞）
        subprocess.run(cmd, cwd=BASE_DIR)
    except KeyboardInterrupt:
        print("\n\n✅ 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Pelican 博客自动构建和本地服务器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python app.py              # 使用默认端口 8000，启用自动重载
  python app.py -p 8001     # 使用端口 8001，启用自动重载
  python app.py -p 8080 --no-reload  # 使用端口 8080，不启用自动重载
        """
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8000,
        help='服务器端口号 (默认: 8000)'
    )
    
    parser.add_argument(
        '--no-reload',
        action='store_true',
        help='禁用自动重载模式'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='pelicanconf.py',
        help='使用的配置文件 (默认: pelicanconf.py)'
    )
    
    parser.add_argument(
        '--skip-build',
        action='store_true',
        help='跳过构建步骤，直接启动服务器'
    )
    
    args = parser.parse_args()
    
    # 检查虚拟环境
    if not check_virtualenv():
        sys.exit(1)
    
    # 构建网站（除非跳过）
    if not args.skip_build:
        if not build_site(args.config):
            print("\n❌ 构建失败，无法启动服务器")
            sys.exit(1)
    else:
        print("⏭️  跳过构建步骤")
    
    # 启动服务器
    start_server(
        port=args.port,
        autoreload=not args.no_reload
    )


if __name__ == '__main__':
    main()

