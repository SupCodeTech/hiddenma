# 论文复现工程：共享转移混合 HMM 的时间一致后验区间与精确极值认证

[English README](README.md)

**版本 0.2.0：论文方法的精确算法参考实现与小规模复现包。它不重新生成论文表格中的全部数值；论文的模拟输出见 Zenodo：https://doi.org/10.5281/zenodo.24462482**

本工程依据用户提供的论文正文 `manuscript.tex`、补充材料 `supplementary_material.tex` 和 Fig1，给出一个**可以直接运行、测试、生成并回放精确证书**的 Python 项目，主要实现论文的统计层、数值层以及一个秩亏可识别目标示例。**核心求解器只使用 Python 标准库**，不需要外部求解服务。

论文标题：*Functional identifiability and certified time-uniform posterior inference in hidden Markov models with transition matrices mixed from known modes*。

## 一、快速开始

需要 Python **3.10+**，推荐 Python 3.11。

```bash
# 进入解压后的工程目录
git clone https://github.com/SupCodeTech/hiddenma.git
cd hiddenma

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

这里的 `--model finance` 仅使用论文冻结的**矩阵参数**，通过给定随机数种子模拟一个新观测序列；**不会声称复现 2022—2024 年实际金融实验**。

### 对自己提供的观测序列计算区间

输入 `examples/observations.json`，内容为 `[0, 1, 1, 0, ...]` 这样的整数数组；各类别编号从 **0** 开始（论文公式中常用从 1 开始的符号）。

```bash
python run.py certify \
  --model examples/rank_deficient.json \
  --observations examples/observations.json \
  --alpha 1/20 --epsilon 1/200 \
  --max-memory 18 --max-cells 48 \
  --output my_certificate.json

python run.py verify my_certificate.json
```

注意 `--epsilon 1/200` 等于 0.005；`--alpha 1/20` 等于 0.05。可以传入 `--max-seconds 10` 设置运行时预算，若预算耗尽，会返回 `resource-limited`，**不会冒充认证成功**。

### 运行简化版数值实验

```bash
python examples/experiment_e1.py
python examples/experiment_e2.py
python examples/finance_from_symbols.py examples/observations.json
```

E1 用一条模拟轨迹展示参数直径 `D_theta`、观测特征直径 `D_q` 与目标后验区间；E2 检查模拟路径上的时间一致参数包含情况。这些是方便检查方法的**小规模示例**，不等价于原文中全部 Monte Carlo 重复次数或数据结果。

## 二、论文公式和工程模块对照

| 论文内容 | 代码位置 | 工程能力 |
| --- | --- | --- |
| 混合转移矩阵、过滤递推 `(1)-(4)` | `hmmcert/model.py` | 精确有理数 HMM 前向过滤、似然、采样 |
| 目标的有限字长等价判别（固定参数对） | `hmmcert/identifiability.py` | 基于张量向量张成空间的精确判别（多项式时间，字长自动不超过 `S²−1`），保留穷举版本作对照 |
| 时间一致块频率半径 `eta_any` | `hmmcert/confidence.py` | 通用正 HMM 的块频率半径和单点区域成员判别 |
| 混合似然比置信域 `C_LR` | `hmmcert/confidence.py` | 给定**预先固定的离散参考分布**，精确有理数似然比和成员判别 |
| 仿射刷新稳态符号 `q_a(theta)` | `hmmcert/model.py` | 使用精确线性方程求解稳态，获得仿射签名 |
| `H`、`eta_ideal`、`eta` 与 `C_obs` | `hmmcert/confidence.py` | 根式的有理数向外包络、`Q_t` 栅格向外取整、置信域线性不等式 |
| 置信多面体和单纯形覆盖（任意 K≥2） | `hmmcert/geometry.py` | K≤3：精确半空间裁剪与扇形三角化；K≥4：精确顶点枚举与面格上的 pulling 三角化；最长边平分 |
| 区域收缩 oracle、遗忘上界 `E_V(m)` | `hmmcert/bernstein.py` | 严格有理数的转移矩阵包络、交叉比、`kappa_V`、`log R_V` 上包络 |
| Bernstein 比率上下界、整数递推 | `hmmcert/bernstein.py` | 整数无分数递推及独立 Fraction 对照实现 |
| 全局界 `L, U, Lbar, Uunder`、双侧 gap | `hmmcert/solver.py` | 自适应单纯形细分、有效见证点、精确极值夹逼及资源状态 |
| 证书重算与核验 | `hmmcert/certificate.py` | 重建输入置信域、回放几何划分、重算整数递推和 gap、SHA-256 校验 |
| 原文 E1、E6 的固定模型参数 | `examples/*.json` | 原文秩亏 3 状态模型、金融 3 状态冻结参数 |

## 三、输出字段和认证的真正含义

每个成功生成的 JSON 文件包含模型、观测序列、置信水平、精度和预算、置信域顶点、最终单纯形覆盖、平分轨迹、外区间和内见证界，分数以 `"numerator/denominator"` 形式保存。

对于每个返回时间点 `t`，如果 `status="certified"`，工程已逐项核对：

- `L <= inf_{theta in C} F_t(theta) <= Lbar`；
- `Uunder <= sup_{theta in C} F_t(theta) <= U`；
- `max(Lbar - L, U - Uunder) <= epsilon`。

**重要：** 论文区分三层概念：

1. **统计覆盖**：若原文所要求的固定输入、正概率、共享固定混合权重等假设成立，观测置信域具有时间一致的参数包含保证（概率不小于 `1-alpha`）。
2. **数值认证**：独立于统计假设，对当前给定的固定有理数模型及非空有理数置信域，给出严格的后验极值外包络。达到双侧 gap 才写 `certified`。
3. **模型正确性**：本工程**不为估计出的金融模式、发射概率或数据加工步骤提供模型错设的统计保证**。

此外，**`[L,U]` 的长度表示目标后验范围，不是优化误差**。优化误差是 `gap_lower` 和 `gap_upper`。区域为零空间时标 `empty-region`；预算不够标 `resource-limited`，其已计算的外包络仍是数学上有效的，但**没有所请求的绝对精度证书**。

SHA-256 的作用是检验本 JSON 内容是否被意外修改，**不是作者签名、链上证明或恶意修改不可伪造的证明**。验证器会依据 JSON 自带的输入独立重算每个数值夹逼步骤；若外部输入本身错误，证书不会把它变成正确的模型。

## 四、覆盖范围和局限（请特别注意）

**已经实现：**

- 任意有限状态数 `S`、有限观测字母数 `b` 和模式数 `K` 的正 HMM 基本过滤、采样、似然及块频率/似然比成员判别。
- 任意有限 `S`、`b` 和**任意 `K≥2`** 的严格正、有理数仿射刷新 HMM：精确生成置信多面体及单纯形分解（K≥4 使用顶点枚举与 pulling 三角化；计算量随 K 和记忆窗口迅速增长）。
- 参数域允许出现低维、线段、单点或空置信集；算法遇到不支持的高维几何明确报错。
- 有理数 Bernstein 系数比率、整数递推、区域收缩 oracle、精确顶点见证、在固定内存窗口之外的严格遗忘误差。

**没有实现，不应冒称已实现：**

- 任意非仿射、半代数的全局量词消去（QE/CAD）、一般 `C_LR` 或一般块频率曲面上的**全局极值求解器**；目前只提供这些区域的成员判断。
- 对所有参数对同时进行全局 fiber invariance 的量词消去证明；只实现给定参数对的有限字判别。E1 的强可合并性证明来自论文的数学结构。
- 作者论文中的全部 E1—E6 实验数据、300 次重复试验、独立金融 2022—2024 原始观测、MLE/贝叶斯标定重算，以及 `744/756` 的原始逐日认证复现。上传的 TeX 是论文描述**而不是原始轨迹、市场数据和认证日志**。
- 正参数估计误差的推断；模型矩阵均假定已给定且可信。

若要复现所有数值表格，需要补充论文**真实数据、随机数轨迹 / 精确输入记录、参数拟合细节和原始证书**，并对一般似然比区域实现量词消去或实根隔离。本工程不会把新模拟得到的输出混同于论文报告数字。

## 五、精确计算的实现选择

1. **有理数输入**：JSON 请使用 `"0.85"`、`"17/100"` 等字符串，不直接传 Python 二进制浮点数。`Fraction` 表示所有概率、顶点、系数和证书界。
2. **根式向外舍入**：精确整数平方根给出向上的十进制有理数根界，然后按论文定义的 `Q_t` 向外取整。这个实现可能比论文精确实数半径多保守一个 `1/Q_t` 栅格，但不会缩窄置信域。
3. **对数向外舍入**：用 `log(x)=2 atanh((x-1)/(x+1))` 的正项级数和严格尾项上界，并按 2 的幂约化，避免把不受控的浮点结果当成证书。
4. **Bernstein 整数 lift**：按论文的多指标单项式递推构造每一步的整数矩阵 `Q_n D_n K_v.T`，最终比率中公共整数比例因子精确消去。
5. **遗忘误差**：使用 `R_phi * log(R_V)/2 * kappa_V**(m-1)` 的保守上界，结合 `R_phi` 作为绝对上限。若 `m>=t` 则使用全史且误差为零。
6. **自适应细分**：基于影响当前全局极值的单纯形选择最长边二分；精确顶点见证提高内界；达到所需两侧 gap 才认证。
7. **回放验证**：置信域由原始观测独立重构，几何覆盖由初始三角化加上记录的精确二分操作生成；不凭空信任证书里列出的单纯形。

## 六、工程目录

```text
hiddenma/
├── run.py                         # 一键入口
├── pyproject.toml                 # 可安装、无额外核心依赖
├── README.md                      # 本中文说明
├── hmmcert/
│   ├── __main__.py                # demo / certify / verify / inspect 命令
│   ├── exact.py                   # Fraction、矩阵求解、sqrt/log 严格有理数上界
│   ├── model.py                   # 通用共享混合 HMM + 仿射刷新模型
│   ├── identifiability.py         # 有限字目标等价与敏感度
│   ├── confidence.py              # 3 种时间一致统计置信区域
│   ├── geometry.py                # 任意 K 的精确有理数几何
│   ├── bernstein.py               # 区域收缩 + 整数 lift + 端点界
│   ├── solver.py                  # 双侧 gap 认证的全局细分求解器
│   └── certificate.py             # 证书创建与完整几何 / 数值回放
├── examples/
│   ├── rank_deficient.json        # 论文 E1 的精确秩亏模型
│   ├── finance.json               # 论文 E6 的固定金融矩阵
│   ├── observations.json          # 用户自定义输入示例
│   ├── experiment_e1.py          # 简化版 E1 实验
│   ├── experiment_e2.py          # 简化版 E2 实验
│   ├── experiment_e4_scaling.py  # E4 风格规模实验（含 K=4，整数/有理递推对比）
│   ├── four_mode.json            # K=4 演示模型
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

**安全和性能提醒**：精确大整数随窗口长度、模式数增长，`binomial(m + K - 1, K - 1)` 项可能增加很快。第一次测试建议使用 `--length 12 --max-memory 12`。默认分数计算不是面向无限观测序列的常数内存实时系统。对于任意长期数据，需要窗口/预算策略和更多性能工程。

## 八、0.2.0 版本更新

- 认证优化支持任意 `K≥2`（此前仅 `K≤3`），新增 `four_mode` 演示模型。
- 有限字等价判别改为张成空间算法：精确且为多项式时间；金融模型最坏情形从约 36 秒降到毫秒级。
- 每个单元缓存转移矩阵：求解提速 2–3 倍，精确结果逐位相同。
- 证书核验新增不复用求解器路径的交叉检查：顶点可行性、独立计算的区域体积、整数与有理递推结果完全一致；新证书为 `hmmcert-v2`，旧 v1 证书仍可核验。
- 命令行：`--paper-indexed`（论文 1 起始符号）、输入校验、`verify --no-cross-check`。
- 测试增至 33 个，并新增 E4 风格规模示例。
