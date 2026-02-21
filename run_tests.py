#!/usr/bin/env python
"""Script helper para executar testes com diferentes configurações."""

import subprocess
import sys
import argparse


def run_command(cmd):
    """Executa comando e retorna status."""
    print(f"[>] Executando: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Executar testes com diferentes configurações"
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=["all", "http", "db", "cli", "web", "coverage", "watch"],
        help="Qual conjunto de testes rodar"
    )
    
    args = parser.parse_args()
    
    base_cmd = [sys.executable, "-m", "pytest"]
    
    commands = {
        "all": base_cmd + ["-v"],
        "http": base_cmd + ["-v", "tests/test_http.py"],
        "db": base_cmd + ["-v", "tests/test_db.py"],
        "cli": base_cmd + ["-v", "tests/test_cli.py"],
        "web": base_cmd + ["-v", "tests/test_web.py"],
        "coverage": base_cmd + ["--cov=.", "--cov-report=html", "--cov-report=term"],
        "watch": base_cmd + ["-v", "--looponfail"],
    }
    
    if args.command not in commands:
        print(f"[!] Comando desconhecido: {args.command}")
        sys.exit(1)
    
    exit_code = run_command(commands[args.command])
    
    if exit_code == 0:
        print("\n[OK] Testes passaram!")
    else:
        print(f"\n[FAIL] Testes falharam (exit code: {exit_code})")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
