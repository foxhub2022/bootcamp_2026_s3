"""非对称加密实践：RSA 与 ECC (ECDSA) 签名与验证。

本脚本演示：
1. PoW 工作量证明：寻找符合前导 0 要求的 (昵称 + nonce)。
2. 生成非对称加密公私钥对（分别实践 RSA 与区块链常用的 ECC secp256k1）。
3. 使用私钥对 PoW 产生的有效内容 (nickname + nonce) 进行数字签名。
4. 使用对应公钥进行签名验证（包括正常验证与防篡改验证）。
"""

import os
import sys

# 兼容 Windows 控制台编码
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa

# 确保能正确引入同目录下的 pow_fox 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from pow_fox import PREFIX, mine
except ImportError:
    import hashlib
    import random
    import time

    PREFIX = "fox"
    NONCE_UPPER = 2**32

    def mine(leading_zeros: int) -> tuple[int, str, str, float, int]:
        target = "0" * leading_zeros
        nonce = random.randrange(NONCE_UPPER)
        attempts = 0
        start = time.perf_counter()
        while True:
            content = f"{PREFIX}{nonce}"
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            attempts += 1
            if digest.startswith(target):
                elapsed = time.perf_counter() - start
                return nonce, content, digest, elapsed, attempts
            nonce += 1


# ==========================================
# 1. RSA (Rivest–Shamir–Adleman)
# ==========================================
def rsa_demo(message: str) -> None:
    print("=" * 65)
    print("【实践一：RSA 非对称加密签名与验证】")
    print("=" * 65)

    # 1. 生成 RSA 2048 位密钥对
    print("[1] 正在生成 RSA 2048 位公私钥对...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # 导出并展示 PEM 格式公钥
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    print("RSA 公钥 (PEM 格式):\n" + pub_pem.strip())

    # 2. 用私钥进行签名（采用现代安全的 PSS 填充与 SHA-256）
    data_bytes = message.encode("utf-8")
    print(f"\n[2] 准备签名的待签数据 (nickname + nonce): {message}")
    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    print("私钥签名成功！")
    print(f"签名长度: {len(signature)} 字节 (2048 位)")
    print(f"签名 Hex (前 64 字符): {signature.hex()[:64]}...")

    # 3. 用公钥验证签名
    print("\n[3] 使用 RSA 公钥验证签名...")
    try:
        public_key.verify(
            signature,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        print("[OK] RSA 公钥验证成功：签名有效，数据未被篡改，确由私钥持有者签发！")
    except InvalidSignature:
        print("[FAIL] RSA 公钥验证失败：签名无效！")

    # 4. 防篡改测试：数据被恶意篡改后的验证结果
    tampered_data = (message + "_tampered").encode("utf-8")
    print(f"\n[4] 防篡改测试：尝试验证被篡改的数据: '{tampered_data.decode('utf-8')}'")
    try:
        public_key.verify(
            signature,
            tampered_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        print("[WARN] 异常：篡改数据竟然验证通过！")
    except InvalidSignature:
        print("[防篡改成功] 篡改后的数据无法通过公钥验证 (已拦截 InvalidSignature)！")
    print()


# ==========================================
# 2. ECC (Elliptic Curve Cryptography - secp256k1)
# ==========================================
def ecc_demo(message: str) -> None:
    print("=" * 65)
    print("【实践二：ECC 椭圆曲线 (secp256k1，区块链比特币/以太坊标准) 签名与验证】")
    print("=" * 65)

    # 1. 生成 ECC secp256k1 密钥对
    print("[1] 正在生成 ECC (SECP256K1) 公私钥对...")
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()

    # 导出并展示 PEM 格式公钥
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    print("ECC 公钥 (PEM 格式):\n" + pub_pem.strip())

    # 2. 用私钥进行 ECDSA 签名
    data_bytes = message.encode("utf-8")
    print(f"\n[2] 准备签名的待签数据 (nickname + nonce): {message}")
    signature = private_key.sign(
        data_bytes,
        ec.ECDSA(hashes.SHA256()),
    )
    print("私钥签名成功！")
    print(f"签名长度: {len(signature)} 字节 (DER 编码)")
    print(f"签名 Hex: {signature.hex()}")

    # 3. 用公钥验证签名
    print("\n[3] 使用 ECC 公钥验证签名...")
    try:
        public_key.verify(
            signature,
            data_bytes,
            ec.ECDSA(hashes.SHA256()),
        )
        print("[OK] ECC 公钥验证成功：ECDSA 签名有效，身份与数据校验通过！")
    except InvalidSignature:
        print("[FAIL] ECC 公钥验证失败：签名无效！")

    # 4. 防篡改测试：数据被恶意篡改后的验证结果
    tampered_data = (message + "_tampered").encode("utf-8")
    print(f"\n[4] 防篡改测试：尝试验证被篡改的数据: '{tampered_data.decode('utf-8')}'")
    try:
        public_key.verify(
            signature,
            tampered_data,
            ec.ECDSA(hashes.SHA256()),
        )
        print("[WARN] 异常：篡改数据竟然验证通过！")
    except InvalidSignature:
        print("[防篡改成功] 篡改后的数据无法通过公钥验证 (已拦截 InvalidSignature)！")
    print()


def main() -> None:
    print("[Step 0] 运行 PoW 工作量证明（寻找符合 4 个前导 0 的 昵称 + nonce）...")
    leading_zeros = 4
    nonce, content, digest, elapsed, attempts = mine(leading_zeros)
    print(f"   - 目标难度: {leading_zeros} 个前导 0")
    print(f"   - 命中原文: {content} (前缀/昵称: '{PREFIX}', nonce: {nonce})")
    print(f"   - 哈希摘要: {digest}")
    print(f"   - 耗时: {elapsed:.4f} 秒, 尝试次数: {attempts}\n")

    # 针对符合 PoW 的 content 依次进行 RSA 与 ECC 实践
    rsa_demo(content)
    ecc_demo(content)


if __name__ == "__main__":
    main()
