# MLB薪資市場效率分析：計量財務指標

---

## 目錄

1. [前言](#1-前言)
2. [動態面板效率指標 (DPEI)](#2-動態面板效率指標-dpei)
3. [門檻效應超額回報模型 (TERM)](#3-門檻效應超額回報模型-term)
4. [分量迴歸效率指數 (QREI)](#4-分量迴歸效率指數-qrei)
5. [處理效應市場調整模型 (TEMAM)](#5-處理效應市場調整模型-temam)
---

## 1. 前言

本文件定義五個計量財務指標，用於分析MLB薪資市場的效率性、異質性與結構變化。這些指標借鑑了**動態面板資料模型**、**門檻迴歸**、**分量迴歸**、**處理效應模型**與**貝氏分層模型**等計量經濟學前沿方法。

---

## 2. 動態面板效率指標 (DPEI)

### 2.1 定義

動態面板效率指標（Dynamic Panel Efficiency Index, DPEI）考慮球員薪資的慣性效應（persistence）與個體異質性，使用動態面板資料模型分離短期衝擊與長期均衡。

### 2.2 模型設定

#### 2.2.1 動態面板模型

$$ \ln(\text{Salary}_{it}) = \alpha_i + \rho \ln(\text{Salary}_{i,t-1}) + \beta_1 \text{WAR}_{it} + \beta_2 \text{WAR}_{it}^2 + \gamma_1 \text{Age}_{it} + \gamma_2 \text{Age}_{it}^2 + \lambda_t + \varepsilon_{it} $$

其中：
- $i = 1, \dots, N$：球員編號
- $t = 1, \dots, T$：時間（賽季）
- $\alpha_i$：球員固定效應（捕捉天賦、態度等不隨時間改變的特質）
- $\lambda_t$：時間固定效應（捕捉聯盟環境變化、通貨膨脹）
- $\varepsilon_{it}$：干擾項，假設 $E[\varepsilon_{it}] = 0$，$E[\varepsilon_{it}\varepsilon_{js}] = \sigma^2$ 若 $i=j$ 且 $t=s$，否則為 0

#### 2.2.2 長期均衡關係

由動態模型可推導長期均衡薪資：

$$ \ln(\text{Salary}_{it}^*) = \frac{\alpha_i + \beta_1 \text{WAR}_{it} + \beta_2 \text{WAR}_{it}^2 + \gamma_1 \text{Age}_{it} + \gamma_2 \text{Age}_{it}^2 + \lambda_t}{1 - \rho} $$

#### 2.2.3 調整速度

半數調整期（half-life）衡量偏離均衡後的回復速度：

$$ \text{Half-life} = \frac{\ln(0.5)}{\ln(\rho)} $$

當 $\rho$ 越接近 1，調整速度越慢，市場越僵固。

### 2.3 估計方法

由於落後項 $\ln(\text{Salary}_{i,t-1})$ 與固定效應 $\alpha_i$ 相關，OLS估計會產生偏誤。使用Arellano-Bond GMM估計：

#### 2.3.1 一階差分消除固定效應

$$ \Delta \ln(\text{Salary}_{it}) = \rho \Delta \ln(\text{Salary}_{i,t-1}) + \beta_1 \Delta \text{WAR}_{it} + \beta_2 \Delta \text{WAR}_{it}^2 + \gamma_1 \Delta \text{Age}_{it} + \gamma_2 \Delta \text{Age}_{it}^2 + \Delta \lambda_t + \Delta \varepsilon_{it} $$

#### 2.3.2 工具變數

使用 $\ln(\text{Salary}_{i,t-2}), \ln(\text{Salary}_{i,t-3}), \dots$ 作為 $\Delta \ln(\text{Salary}_{i,t-1})$ 的工具變數，因為這些變數與 $\Delta \ln(\text{Salary}_{i,t-1})$ 相關，但與 $\Delta \varepsilon_{it}$ 不相關。

#### 2.3.3 動差條件

$$ E[\ln(\text{Salary}_{i,t-s}) \Delta \varepsilon_{it}] = 0, \quad s \geq 2, t = 3, \dots, T $$

#### 2.3.4 過度識別檢定

使用Sargan檢定檢驗工具變數的有效性：

$$ J = \left(\frac{1}{N} \sum_{i=1}^N \mathbf{Z}_i' \hat{\mathbf{\varepsilon}}_i\right)' \hat{\mathbf{V}}^{-1} \left(\frac{1}{N} \sum_{i=1}^N \mathbf{Z}_i' \hat{\mathbf{\varepsilon}}_i\right) \xrightarrow{d} \chi^2_{L-K} $$

其中 $L$ 是工具變數個數，$K$ 是參數個數。

### 2.4 DPEI定義

$$ \text{DPEI} = \underbrace{\frac{|\hat{\rho} - \rho^*|}{\rho^*}}_{\text{慣性偏離}} \times \underbrace{(1 - \hat{\beta}_1)}_{\text{短期效率}} \times \underbrace{\exp\left(-\frac{1}{\hat{T}} \sum_{i=1}^N \sum_{t=1}^T |\ln(\text{Salary}_{it}) - \ln(\text{Salary}_{it}^*)|\right)}_{\text{均衡偏離}} $$

其中 $\rho^*$ 是效率市場下的理論慣性係數（通常設為 0，表示薪資應立即調整）。

### 2.5 假設檢定

#### 2.5.1 無慣性效應檢定

檢定 $H_0: \rho = 0$：

$$ t_\rho = \frac{\hat{\rho}}{\text{SE}(\hat{\rho})} \xrightarrow{d} \mathcal{N}(0, 1) $$

#### 2.5.2 市場效率檢定

效率市場要求 $\beta_1 = 1$（薪資與WAR成比例）：

$$ H_0: \beta_1 = 1 $$

Wald統計量：

$$ W = \frac{(\hat{\beta}_1 - 1)^2}{\text{Var}(\hat{\beta}_1)} \xrightarrow{d} \chi^2_1 $$

### 2.6 經濟意義

- **DPEI < 0.2**：高度效率市場（快速調整、慣性低）
- **0.2 ≤ DPEI < 0.4**：中度效率
- **0.4 ≤ DPEI < 0.6**：低度效率
- **DPEI ≥ 0.6**：市場僵固（調整極慢、存在套利機會）

### 2.7 設定理由

1. **動態結構**：傳統靜態模型忽略薪資調整的動態過程，DPEI捕捉了市場的「摩擦」程度。

2. **個體異質性**：透過固定效應 $\alpha_i$ 控制球員不可觀測的天賦差異，避免遺漏變數偏誤。

3. **慣性效應**：$\rho$ 衡量薪資的慣性，反映合約長度、交易成本等市場摩擦。

4. **GMM估計**：解決動態面板的內生性問題，提供一致估計量。

5. **均衡偏離**：計算實際薪資與長期均衡的距離，衡量市場定價效率。

---

## 3. 門檻效應超額回報模型 (TERM)

### 3.1 定義

門檻效應超額回報模型（Threshold Effect Return Model, TERM）允許WAR與薪資的關係在不同區間有不同斜率，識別「明星溢價」的門檻值。

### 3.2 模型設定

#### 3.2.1 單一門檻模型

$$ \text{Salary}_i = \begin{cases} 
\alpha_1 + \beta_1 \text{WAR}_i + \gamma_1 \text{Age}_i + \delta_1 \text{Experience}_i + \varepsilon_i & \text{if WAR}_i \leq \tau \\
\alpha_2 + \beta_2 \text{WAR}_i + \gamma_2 \text{Age}_i + \delta_2 \text{Experience}_i + \varepsilon_i & \text{if WAR}_i > \tau
\end{cases} $$

其中 $\tau$ 是未知門檻值。

#### 3.2.2 雙門檻模型（Hansen, 2000）

$$ \text{Salary}_i = \begin{cases} 
\alpha_1 + \beta_1 \text{WAR}_i + \mathbf{X}_i'\boldsymbol{\theta} + \varepsilon_i & \text{if WAR}_i \leq \tau_1 \\
\alpha_2 + \beta_2 \text{WAR}_i + \mathbf{X}_i'\boldsymbol{\theta} + \varepsilon_i & \text{if } \tau_1 < \text{WAR}_i \leq \tau_2 \\
\alpha_3 + \beta_3 \text{WAR}_i + \mathbf{X}_i'\boldsymbol{\theta} + \varepsilon_i & \text{if WAR}_i > \tau_2
\end{cases} $$

### 3.3 估計方法

使用網格搜尋（grid search）最小化殘差平方和：

$$ \hat{\tau} = \arg\min_{\tau \in \Gamma} S_n(\tau) $$

其中 $S_n(\tau)$ 是給定門檻值 $\tau$ 的殘差平方和。

### 3.4 門檻效應檢定

檢定虛無假設 $H_0: \beta_1 = \beta_2$（無門檻效應）：

$$ F_n = \frac{S_0 - S_n(\hat{\tau})}{\hat{\sigma}^2} $$

其中 $S_0$ 是無門檻模型的殘差平方和。

由於 $\tau$ 在虛無假設下未被識別，使用拔靴法（bootstrap）計算p值：

$$ \hat{p} = \frac{1}{B} \sum_{b=1}^B \mathbb{I}(F_n^{(b)} > F_n) $$

### 3.5 TERM定義

$$ \text{TERM}_i = \begin{cases}
\frac{\hat{\beta}_2 - \hat{\beta}_1}{\hat{\beta}_1} \times \text{WAR}_i & \text{if WAR}_i > \hat{\tau} \\
0 & \text{otherwise}
\end{cases} $$

### 3.6 明星溢價率

明星溢價率（Star Premium Rate）定義為：

$$ \text{SPR} = \frac{\hat{\beta}_2 - \hat{\beta}_1}{\hat{\beta}_1} \times 100\% $$

### 3.7 信賴區間建構

使用拔靴法建構門檻值的信賴區間：

$$ \text{CI}_{1-\alpha} = \{\tau: LR_n(\tau) \leq c(\alpha)\} $$

其中：

$$ LR_n(\tau) = \frac{S_n(\tau) - S_n(\hat{\tau})}{\hat{\sigma}^2} $$

$c(\alpha)$ 是 $LR_n(\tau)$ 的 $(1-\alpha)$ 分位數。

### 3.8 經濟意義

- **SPR > 50%**：明星球員享有超過50%的溢價（贏者全拿市場）
- **20% < SPR ≤ 50%**：中度溢價
- **SPR ≤ 20%**：小幅溢價（市場相對理性）

### 3.9 設定理由

1. **非線性關係**：傳統線性模型假設WAR對薪資的邊際效果固定，但經濟理論預期明星球員可能有更高邊際價值（稀缺性、市場吸引力）。

2. **內生門檻**：門檻值 $\tau$ 由數據決定，而非主觀設定（如WAR=5），符合計量經濟學的嚴謹要求。

3. **識別策略**：透過Hansen檢定確認門檻效應的統計顯著性，避免假性相關。

4. **政策意涵**：SPR可作為評估勞資協議中「超級巨星條款」的參考依據。

5. **穩健推論**：使用拔靴法建構信賴區間，不依賴漸近常態假設。

---

## 4. 分量迴歸效率指數 (QREI)

### 4.1 定義

分量迴歸效率指數（Quantile Regression Efficiency Index, QREI）使用分量迴歸（quantile regression）分析不同薪資水準下，WAR對薪資的邊際影響是否存在差異。

### 4.2 模型設定

#### 4.2.1 分量迴歸模型

對於分量 $\tau \in (0,1)$：

$$ Q_{\tau}(\text{Salary}_i | \text{WAR}_i, \mathbf{X}_i) = \alpha_{\tau} + \beta_{\tau} \text{WAR}_i + \mathbf{X}_i'\boldsymbol{\gamma}_{\tau} $$

其中 $Q_{\tau}(Y|X)$ 是給定 $X$ 下 $Y$ 的條件 $\tau$ 分位數。

#### 4.2.2 估計方法

最小化加權絕對離差：

$$ \min_{\alpha_{\tau}, \beta_{\tau}, \boldsymbol{\gamma}_{\tau}} \sum_{i=1}^n \rho_{\tau}(\text{Salary}_i - \alpha_{\tau} - \beta_{\tau} \text{WAR}_i - \mathbf{X}_i'\boldsymbol{\gamma}_{\tau}) $$

其中 $\rho_{\tau}(u) = u(\tau - \mathbb{I}(u < 0))$ 是檢查函數（check function）。

### 4.3 分量迴歸的漸近性質

**定理 4.1**：在正則條件下，分量迴歸估計量 $\hat{\boldsymbol{\beta}}_{\tau}$ 是 $\sqrt{n}$-一致的且漸近常態：

$$ \sqrt{n}(\hat{\boldsymbol{\beta}}_{\tau} - \boldsymbol{\beta}_{\tau}) \xrightarrow{d} \mathcal{N}\left(0, \tau(1-\tau) \mathbf{D}_{\tau}^{-1} \mathbf{\Omega} \mathbf{D}_{\tau}^{-1}\right) $$

其中 $\mathbf{D}_{\tau} = \mathbb{E}[f_{\varepsilon_{\tau}}(0|\mathbf{X}) \mathbf{X} \mathbf{X}']$，$\mathbf{\Omega} = \mathbb{E}[\mathbf{X} \mathbf{X}']$。

### 4.4 分量係數的經濟意義

對於不同 $\tau$：

- $\tau = 0.1$：低薪球員（新秀、角色球員）
- $\tau = 0.25$：中低薪球員
- $\tau = 0.5$：中位數球員
- $\tau = 0.75$：中高薪球員
- $\tau = 0.9$：高薪球員（明星、巨星）

### 4.5 QREI定義

$$ \text{QREI} = \underbrace{\frac{1}{K} \sum_{k=1}^K \left|\frac{\hat{\beta}_{\tau_k} - \bar{\hat{\beta}}}{\bar{\hat{\beta}}}\right|}_{\text{係數異質性}} \times \underbrace{\left(1 + \frac{\hat{\beta}_{\tau_H} - \hat{\beta}_{\tau_L}}{\hat{\beta}_{\tau_L}}\right)}_{\text{明星溢價}} \times \underbrace{\Phi\left(\frac{\hat{\beta}_{0.5} - 1}{\hat{\sigma}_{0.5}}\right)}_{\text{中位數效率}} $$

其中：
- $\tau_k$：選擇的 $K$ 個分量
- $\tau_H$：高分位數（如 0.9）
- $\tau_L$：低分位數（如 0.1）
- $\Phi(\cdot)$：標準常態累積分布函數

### 4.6 分量係數相等性檢定

檢定 $H_0: \beta_{\tau_1} = \beta_{\tau_2} = \cdots = \beta_{\tau_K}$：

使用Wald檢定：

$$ W = (\mathbf{R}\hat{\boldsymbol{\beta}})'(\mathbf{R} \hat{\mathbf{V}} \mathbf{R}')^{-1}(\mathbf{R}\hat{\boldsymbol{\beta}}) \xrightarrow{d} \chi^2_{K-1} $$

其中 $\mathbf{R}$ 是限制矩陣，$\hat{\mathbf{V}}$ 是共變異數矩陣估計。

### 4.7 經濟意義

- **QREI < 0.2**：市場對不同薪資水準一視同仁（效率市場）
- **0.2 ≤ QREI < 0.4**：中度異質性
- **0.4 ≤ QREI < 0.6**：顯著異質性
- **QREI ≥ 0.6**：市場存在結構性差異（低薪與高薪市場分割）

### 4.8 設定理由

1. **異質性分析**：傳統迴歸只考慮平均效果，但WAR對低薪球員和高薪球員的影響可能不同。

2. **分量迴歸優勢**：
   - 不受極端值影響（robust to outliers）
   - 不需常態分配假設
   - 提供完整的條件分布資訊

3. **經濟學預期**：
   - 低薪球員：WAR增加可能大幅加薪（從底薪到先發）
   - 高薪球員：WAR增加影響有限（邊際效益遞減）

4. **市場分割檢驗**：若 $\beta_{\tau}$ 隨 $\tau$ 遞減，表示高薪市場效率較低（明星溢價）。

5. **中位數效率**：使用 $\tau=0.5$ 作為市場效率的基準，因為中位數不受極端值影響。

---

## 5. 處理效應市場調整模型 (TEMAM)

### 5.1 定義

處理效應市場調整模型（Treatment Effect Market Adjustment Model, TEMAM）使用處理效應模型估計特定事件（如入選明星賽、獲得獎項）對薪資的因果效應。

### 5.2 模型設定

#### 5.2.1 潛在結果框架

定義：
- $Y_{1i}$：球員 $i$ 接受處理（如入選明星賽）後的薪資
- $Y_{0i}$：球員 $i$ 未接受處理的薪資
- $T_i \in \{0,1\}$：處理變數（1表示接受處理）

觀測到的薪資：

$$ Y_i = T_i Y_{1i} + (1 - T_i) Y_{0i} $$

#### 5.2.2 平均處理效應

$$ \text{ATE} = \mathbb{E}[Y_{1i} - Y_{0i}] $$

#### 5.2.3 處理組平均處理效應

$$ \text{ATT} = \mathbb{E}[Y_{1i} - Y_{0i} | T_i = 1] $$

### 5.3 選擇性偏誤問題

若 $T_i$ 非隨機分配，直接比較 $Y_i|T_i=1$ 和 $Y_i|T_i=0$ 會產生選擇性偏誤：

$$ \mathbb{E}[Y_i|T_i=1] - \mathbb{E}[Y_i|T_i=0] = \text{ATT} + \underbrace{(\mathbb{E}[Y_{0i}|T_i=1] - \mathbb{E}[Y_{0i}|T_i=0])}_{\text{選擇性偏誤}} $$

### 5.4 估計方法

#### 5.4.1 傾向分數匹配法（Propensity Score Matching）

傾向分數：

$$ p(\mathbf{X}_i) = P(T_i = 1 | \mathbf{X}_i) $$

使用Logit或Probit模型估計：

$$ p(\mathbf{X}_i) = \frac{\exp(\mathbf{X}_i'\boldsymbol{\beta})}{1 + \exp(\mathbf{X}_i'\boldsymbol{\beta})} $$

ATT估計量：

$$ \widehat{\text{ATT}} = \frac{1}{n_T} \sum_{i: T_i=1} \left( Y_i - \frac{1}{m} \sum_{j \in \mathcal{C}_m(i)} Y_j \right) $$

其中 $\mathcal{C}_m(i)$ 是與球員 $i$ 傾向分數最接近的 $m$ 個對照組球員。

#### 5.4.2 工具變數法（Instrumental Variables）

尋找工具變數 $Z_i$ 滿足：
1. 相關性：$Z_i$ 與 $T_i$ 相關
2. 排除限制：$Z_i$ 僅透過 $T_i$ 影響 $Y_i$

兩階段最小平方法（2SLS）：

第一階段：$$ T_i = \pi_0 + \pi_1 Z_i + \mathbf{X}_i'\boldsymbol{\pi} + \eta_i $$
第二階段：$$ Y_i = \alpha + \beta \hat{T}_i + \mathbf{X}_i'\boldsymbol{\gamma} + \varepsilon_i $$

### 5.5 處理效應異質性

允許處理效應隨可觀測變數變化：

$$ Y_i = \alpha + \beta T_i + \mathbf{X}_i'\boldsymbol{\gamma} + T_i \times (\mathbf{X}_i - \bar{\mathbf{X}})'\boldsymbol{\delta} + \varepsilon_i $$

則條件平均處理效應：

$$ \text{CATE}(\mathbf{x}) = \hat{\beta} + (\mathbf{x} - \bar{\mathbf{x}})'\hat{\boldsymbol{\delta}} $$

### 5.6 TEMAM定義

$$ \text{TEMAM} = \underbrace{\frac{\widehat{\text{ATT}}}{\bar{Y}_0}}_{\text{明星效應強度}} \times \underbrace{\left(1 - \frac{\widehat{\text{ATT}} - \widehat{\text{ATE}}}{\widehat{\text{ATT}}}\right)}_{\text{選擇性偏誤調整}} \times \underbrace{\exp\left(-\frac{\sum_{i=1}^n |\hat{e}_i|}{n}\right)}_{\text{匹配品質}} $$

其中 $\hat{e}_i$ 是匹配後的殘差。

### 5.7 敏感性分析

檢驗對未觀測混淆變數的敏感性：

$$ \Gamma = \frac{\pi_{ij}}{\pi_{ji}} $$

其中 $\pi_{ij} = \frac{p_i(1-p_j)}{p_j(1-p_i)}$ 是兩個球員接受處理的勝算比（odds ratio）。

若 $\Gamma$ 接近 1，表示結果對未觀測變數不敏感。

### 5.8 經濟意義

- **TEMAM > 0.5**：明星事件對薪資有重大影響（市場高度反應）
- **0.3 < TEMAM ≤ 0.5**：中度影響
- **0.1 < TEMAM ≤ 0.3**：輕度影響
- **TEMAM ≤ 0.1**：市場無反應（效率市場）

### 5.9 設定理由

1. **因果推論**：傳統迴歸只能衡量相關性，TEMAM估計明星事件的因果效應。

2. **選擇性偏誤**：入選明星賽的球員本來就比較強，直接比較會高估明星效應。

3. **傾向分數匹配**：創建統計上可比的對照組，近似隨機實驗。

4. **工具變數**：若找到有效工具變數（如票數接近但未入選），可進一步處理未觀測混淆。

5. **異質性處理效應**：不同類型的球員（投手vs打者）可能從明星賽獲得不同效益。

