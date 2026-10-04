"""Proof of Work: hash "fox" + nonce with SHA-256 until the digest has N leading zeros."""

import hashlib
import time

PREFIX = "fox"


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mine(leading_zeros: int) -> tuple[int, str, str, float]:
    """Search nonce from 0 until the hash starts with `leading_zeros` zeros.

    Returns nonce, hashed content, hex digest, and elapsed seconds.
    """
    target = "0" * leading_zeros
    nonce = 0
    start = time.perf_counter()

    while True:
        content = f"{PREFIX}{nonce}"
        digest = sha256_hex(content)
        if digest.startswith(target):
            elapsed = time.perf_counter() - start
            return nonce, content, digest, elapsed
        nonce += 1


def report(leading_zeros: int, nonce: int, content: str, digest: str, elapsed: float) -> None:
    print(f"目标: {leading_zeros} 个前导 0")
    print(f"花费时间: {elapsed:.6f} 秒")
    print(f"Hash 内容: {content}")
    print(f"Hash 值: {digest}")
    print(f"nonce: {nonce}")
    print(f"尝试次数: {nonce + 1}")
    print()


def main() -> None:
    for leading_zeros in (4, 5):
        nonce, content, digest, elapsed = mine(leading_zeros)
        report(leading_zeros, nonce, content, digest, elapsed)


if __name__ == "__main__":
    main()
