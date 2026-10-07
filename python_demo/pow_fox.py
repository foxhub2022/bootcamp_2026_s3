"""工作量证明（Proof of Work）：把 "fox" 与 nonce 拼接后做 SHA-256，直到哈希出现 N 个前导 0。"""

import hashlib
import random
import time

# 参与哈希的固定前缀，nonce 会接在它后面
PREFIX = "fox"
# nonce 的取值上限（不含），对应 32 位无符号整数
NONCE_UPPER = 2**32


def sha256_hex(text: str) -> str:
    """把文本按 UTF-8 编码后计算 SHA-256，返回十六进制字符串。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mine(leading_zeros: int) -> tuple[int, str, str, float, int]:
    """从随机 nonce 开始递增，直到哈希以指定个数的 0 开头。

    返回找到的 nonce、被哈希的原文、十六进制摘要、耗时（秒），以及尝试次数。
    """
    # 目标前缀，例如 leading_zeros=4 时为 "0000"
    target = "0" * leading_zeros
    # 起点是 [0, 2**32) 里的随机整数，之后每次 +1
    nonce = random.randrange(NONCE_UPPER)
    attempts = 0
    start = time.perf_counter()

    while True:
        # 拼接前缀和当前 nonce，例如 "fox184392"、"fox184393"...
        content = f"{PREFIX}{nonce}"
        # 将内容转成16进制Hash
        digest = sha256_hex(content)
        attempts += 1
        # 命中难度要求后停止搜索
        if digest.startswith(target):
            elapsed = time.perf_counter() - start
            return nonce, content, digest, elapsed, attempts
        nonce += 1


def report(
    leading_zeros: int,
    nonce: int,
    content: str,
    digest: str,
    elapsed: float,
    attempts: int,
) -> None:
    """打印一次挖矿结果：难度、耗时、原文、哈希、nonce 和尝试次数。"""
    print(f"目标: {leading_zeros} 个前导 0")
    print(f"花费时间: {elapsed:.6f} 秒")
    print(f"Hash 内容: {content}")
    print(f"Hash 值: {digest}")
    print(f"nonce: {nonce}")
    print(f"尝试次数: {attempts}")
    print()


def main() -> None:
    # 分别按 4 个、5 个前导 0 挖一次，难度每增加 1，期望尝试次数大约变为 16 倍
    for leading_zeros in (4, 5):
        nonce, content, digest, elapsed, attempts = mine(leading_zeros)
        report(leading_zeros, nonce, content, digest, elapsed, attempts)


if __name__ == "__main__":
    main()
