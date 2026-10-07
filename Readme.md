# 区块链实验：POW 工作量证明与非对称加密 (RSA & ECC) 实践

本实验基于 Python 实践区块链底层的两大核心技术支柱：**工作量证明（Proof of Work，PoW）** 与 **非对称加密数字签名（RSA 与 ECC secp256k1）**。

---

## 一、实验目标

1. **工作量证明 (PoW)**：
   - 结合固定昵称（如 `fox`）与递增/随机 `nonce` 进行 SHA-256 哈希运算。
   - 寻找满足目标前导 0 数量（如 4 个、5 个前导 0）的合法 nonce。
2. **非对称密钥对生成**：
   - 生成 **RSA** (2048 位) 公私钥对。
   - 生成 **ECC**（基于比特币与以太坊标准曲线 `secp256k1`）公私钥对。
3. **私钥签名**：
   - 使用私钥对符合 PoW 条件的原文数据（`nickname + nonce`）进行数字签名。
4. **公钥验证与防篡改验证**：
   - 使用公钥验证签名的有效性。
   - 对篡改后的数据进行验证测试，证明数字签名保障数据完整性与不可伪造性的机制。

---

## 二、环境与依赖准备

本项目使用 Python 3 标准库及工业级加密库 `cryptography`：

```bash
pip install cryptography
```

---

## 三、文件结构说明

```text
bootcamp_2026_s3/
├── Readme.md                          # 实验说明与实验报告文档
└── python_demo/
    ├── pow_fox.py                     # PoW 工作量证明实现
    └── asymmetric_signature.py        # RSA 与 ECC 密钥生成、签名及验证完整实践脚本
```

---

## 四、核心实现与代码解析

### 1. 工作量证明（PoW 挖矿）

在 `python_demo/pow_fox.py` 中，拼接 `nickname` 和 `nonce` 进行 SHA-256 哈希，直到哈希值满足指定数量的前导 0：

```python
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
```

---

### 2. RSA 非对称加密实践

- **算法参数**：2048 位密钥长度，公共指数 $e = 65537$。
- **填充与哈希**：现代安全规范 PSS (Probabilistic Signature Scheme) 结合 SHA-256。

```python
# 1. 生成密钥对
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# 2. 私钥签名
signature = private_key.sign(
    data_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)

# 3. 公钥验证
public_key.verify(
    signature,
    data_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)
```

---

### 3. ECC 椭圆曲线非对称加密实践（区块链行业标准）

- **椭圆曲线**：`secp256k1`（比特币、以太坊等公链底层采用的曲线）。
- **签名算法**：ECDSA (Elliptic Curve Digital Signature Algorithm) + SHA-256。

```python
# 1. 生成密钥对 (secp256k1)
private_key = ec.generate_private_key(ec.SECP256K1())
public_key = private_key.public_key()

# 2. 私钥签名
signature = private_key.sign(
    data_bytes,
    ec.ECDSA(hashes.SHA256()),
)

# 3. 公钥验证
public_key.verify(
    signature,
    data_bytes,
    ec.ECDSA(hashes.SHA256()),
)
```

---

## 五、运行方式

### 1. 运行 PoW 工作量证明脚本
```bash
python python_demo/pow_fox.py
```

### 2. 运行非对称加密签名与验证完整脚本
```bash
python python_demo/asymmetric_signature.py
```

---

## 六、实际运行结果示例

运行 `python python_demo/asymmetric_signature.py` 的完整输出记录：

```text
[Step 0] 运行 PoW 工作量证明（寻找符合 4 个前导 0 的 昵称 + nonce）...
   - 目标难度: 4 个前导 0
   - 命中原文: fox2628324492 (前缀/昵称: 'fox', nonce: 2628324492)
   - 哈希摘要: 000003b53ee9199825d87d0fc2dfb884f47bc7a03d61b82bbba8b6b45e9b9f94
   - 耗时: 0.0953 秒, 尝试次数: 69523

=================================================================
【实践一：RSA 非对称加密签名与验证】
=================================================================
[1] 正在生成 RSA 2048 位公私钥对...
RSA 公钥 (PEM 格式):
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq6KwQpswCvz+7GxCd6hc
G93xSgkvqaCQYlM+Gro8Qlf4eJQnU/vxlax4yq8sKkoxtlnsu6NeZgdMt5gTusiw
JimaHUW371/TaE83TBVClqKKxtkm1RStOcaAZO2xkUcuP2HyuWqNyQh1gmyxIVfs
Y7zMWQxymkXDi5AX1A5ap3y6QBkYQbNtU+uUYIVQ/OXNfENbqq3AgIFgI6DPFcD/
0TDmYJ0xgXfAWDD5wUYAahQ2OdShlcWC+nIfofm9eNB1258929YYpCwsuIQp3NXo
csyGIfNnY8A4IwFcgBwt2bBSc03iR1Wk4sZgSn2HfGsGgWwYd+7uWQxJR5WnGfay
dQIDAQAB
-----END PUBLIC KEY-----

[2] 准备签名的待签数据 (nickname + nonce): fox2628324492
私钥签名成功！
签名长度: 256 字节 (2048 位)
签名 Hex (前 64 字符): 4f7dc473a95c2534e6ece52c6831f014a34d7a89a26b994b5af6ba7891714c7e...

[3] 使用 RSA 公钥验证签名...
[OK] RSA 公钥验证成功：签名有效，数据未被篡改，确由私钥持有者签发！

[4] 防篡改测试：尝试验证被篡改的数据: 'fox2628324492_tampered'
[防篡改成功] 篡改后的数据无法通过公钥验证 (已拦截 InvalidSignature)！

=================================================================
【实践二：ECC 椭圆曲线 (secp256k1，区块链比特币/以太坊标准) 签名与验证】
=================================================================
[1] 正在生成 ECC (SECP256K1) 公私钥对...
ECC 公钥 (PEM 格式):
-----BEGIN PUBLIC KEY-----
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEogMCEClXro05ZGjXA2Jey6/lzgdGE3RI
Nor/+TqcRE2XqhzHfOAdN+1nImZ73NiEKTXKuR69bE5gLCq6S0m/Rg==
-----END PUBLIC KEY-----

[2] 准备签名的待签数据 (nickname + nonce): fox2628324492
私钥签名成功！
签名长度: 72 字节 (DER 编码)
签名 Hex: 304602210094617b29636fea548011b33621aacb2240c0a87afb2058ef25001fa568521b85022100aaf80d7141c2b658a975b01a0affb644a8e3e328ef68518a38789dde6cd5320e

[3] 使用 ECC 公钥验证签名...
[OK] ECC 公钥验证成功：ECDSA 签名有效，身份与数据校验通过！

[4] 防篡改测试：尝试验证被篡改的数据: 'fox2628324492_tampered'
[防篡改成功] 篡改后的数据无法通过公钥验证 (已拦截 InvalidSignature)！
```

---

## 七、RSA 与 ECC 在区块链中的对比分析

| 特性 | RSA (2048 位) | ECC (secp256k1) | 区块链应用建议 |
| :--- | :--- | :--- | :--- |
| **密钥与签名长度** | 签名 256 字节，公钥较长 | 签名约 64~72 字节，公钥仅 33/65 字节 | ECC 显著减少链上存储开销与网络带宽 |
| **计算开销** | 验签快，但签名计算较重 | 签名与密钥生成极快，综合效率高 | ECC 吞吐量更适配高频交易链 |
| **主流区块链支持** | 少见（历史系统、企业 CA） | 比特币（Bitcoin）、以太坊（Ethereum）等标配 | **首选 ECC (secp256k1)** |
| **安全保证** | 基于大整数质因数分解难题 | 基于椭圆曲线离散对数难题 (ECDLP) | 同等安全强度下 ECC 密钥长度小得多 |