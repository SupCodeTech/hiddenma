论文标题：*Functional identifiability and certified time-uniform posterior inference in hidden Markov models with transition matrices mixed from known modes*。

## 一、快速开始

需要 Python **3.10+**，推荐 Python 3.11。

```bash
# 进入解压后的工程目录
cd hmm_paper_code

# 一条命令运行：模拟观测 -> 构造置信域 -> Bernstein 精确优化 -> 保存 JSON 证书 -> 回放
python run.py demo

# 单独验证刚刚生成的证书
python run.py verify demo_certificate.json

# 检查所有测试（需安装 pytest）
python -m pip install -e '.[test]'
python -m pytest -q
```

如果你习惯模块形式，可以直接使用 `python -m hmmcert demo` 或在安装后运行 `hmmcert demo`。

### 使用论文的金融模型（不需要联网）

```bash
python run.py demo --model finance --length 12 --output finance_certificate.json
python run.py verify finance_certificate.json
```

## 六、工程目录

```text
hmm_paper_code/
├── run.py                         # 一键入口
├── pyproject.toml                 # 可安装、无额外核心依赖
├── README.md                      # 本中文说明
├── hmmcert/
│   ├── __main__.py                # demo / certify / verify / inspect 命令
│   ├── exact.py                   # Fraction、矩阵求解、sqrt/log 严格有理数上界
│   ├── model.py                   # 通用共享混合 HMM + 仿射刷新模型
│   ├── identifiability.py         # 有限字目标等价与敏感度
│   ├── confidence.py              # 3 种时间一致统计置信区域
│   ├── geometry.py                # K<=3 的精确有理数几何
│   ├── bernstein.py               # 区域收缩 + 整数 lift + 端点界
│   ├── solver.py                  # 双侧 gap 认证的全局细分求解器
│   └── certificate.py             # 证书创建与完整几何 / 数值回放
├── examples/
│   ├── rank_deficient.json        # 论文 E1 的精确秩亏模型
│   ├── finance.json               # 论文 E6 的固定金融矩阵
│   ├── observations.json          # 用户自定义输入示例
│   ├── experiment_e1.py          # 简化版 E1 实验
│   ├── experiment_e2.py          # 简化版 E2 实验
│   └── finance_from_symbols.py   # 使用金融矩阵处理自定义符号
├── tests/                         # pytest 自动测试
└── paper_sources/                 # 上传的原始 LaTeX 和 Fig1，便于核对
```

## 七、Python API 示例

```python
import json
from fractions import Fraction as F
from hmmcert import AffineRefresh, SolverSettings, solve
from hmmcert.certificate import build_certificate, verify_certificate

model = AffineRefresh.from_dict(json.load(open("examples/rank_deficient.json")))
observations = [0, 1, 1, 0, 1, 0]
result = solve(model, observations, SolverSettings(alpha=F(1,20),epsilon=F(1,200)))
print(result.status, result.bounds, result.gaps)
certificate = build_certificate(model,result)
print(verify_certificate(certificate))
```