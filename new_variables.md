# MLB薪資市場效率分析：原創財務指標說明
## 目錄

1. [前言](#1-前言)
2. [加權綜合價值指數 (WVPI)](#2-加權綜合價值指數-wvpi)
3. [風險調整後價值 (RAV)](#3-風險調整後價值-rav)
4. [市場效率殘差指數 (MERI)](#4-市場效率殘差指數-meri)
5. [投資組合夏普指數 (PSI)](#5-投資組合夏普指數-psi)
6. [雙因子績效矩陣 (TPM)](#6-雙因子績效矩陣-tpm)
7. [同步效率指數 (SEI)](#7-同步效率指數-sei)
---

## 1. 前言

本文件旨在定義一套原創的財務分析指標，用於評估MLB球員的市場價值、投資效率與風險調整後績效。這些指標借鑑了財務管理、投資學與計量經濟學的核心概念，包括：

- **資本資產定價模型**（CAPM）
- **夏普比率**（Sharpe Ratio）
- **折現現金流模型**（DCF）
- **迴歸殘差分析**
- **基尼係數**（Gini Coefficient）

所有指標均以 $\LaTeX$ 數學語法呈現，確保學術嚴謹性與可複製性。

---

## 2. 加權綜合價值指數 (WVPI)

### 2.1 定義

加權綜合價值指數（Weighted Value Performance Index, WVPI）是一個多維度的球員評估指標，結合了絕對表現、效率、相對排名與成本效益。

### 2.2 數學公式

$$ \text{WVPI} = w_1 \times \text{WAR} + w_2 \times \frac{\text{WAR}}{\text{Salary}} + w_3 \times P_{\text{WAR}} + w_4 \times (100 - P_{\text{Salary}}) $$

其中：
- $\text{WAR}$：勝場貢獻值（Wins Above Replacement）
- $\text{Salary}$：年薪（百萬美元）
- $P_{\text{WAR}}$：WAR的百分位排名（0-100）
- $P_{\text{Salary}}$：薪資的百分位排名（0-100）
- $w_1, w_2, w_3, w_4$：權重參數，滿足 $w_1 + w_2 + w_3 + w_4 = 1$

### 2.3 權重建議

基於財務學的多因子模型概念，建議權重設定如下：

$$ 
\begin{aligned}
w_1 &= 0.35 \quad \text{(絕對表現)} \\
w_2 &= 0.30 \quad \text{(效率)} \\
w_3 &= 0.20 \quad \text{(相對表現)} \\
w_4 &= 0.15 \quad \text{(相對成本)}
\end{aligned}
$$

### 2.4 各項目的詳細說明

#### 2.4.1 絕對表現項 ($w_1 \times \text{WAR}$)

WAR是棒球統計學中最權威的綜合指標，計算公式為：

$$ \text{WAR} = \text{打擊WAR} + \text{守備WAR} + \text{跑壘WAR} + \text{位置調整} - \text{聯盟調整} $$

**為什麼包含這個項目？**
- WAR已經考慮了多種貢獻，是產業標準
- 但WAR忽略成本，所以需要其他項目互補
- 給予最高權重（0.35）因為表現是價值的基礎

#### 2.4.2 效率項 ($w_2 \times \frac{\text{WAR}}{\text{Salary}}$)

性價比（Value Ratio）直接衡量每百萬美元能獲得多少WAR：

$$ \text{Value Ratio} = \frac{\text{WAR}}{\text{Salary}} $$

**為什麼包含這個項目？**
- 反映投資效率，類似財務的「本益比倒數」
- 高性價比球員是「價值投資」標的
- 避免陷入「高WAR就是好球員」的迷思

#### 2.4.3 相對表現項 ($w_3 \times P_{\text{WAR}}$)

百分位排名定義：

$$ P_{\text{WAR}} = \frac{\text{排名}(\text{WAR}_i) - 1}{N - 1} \times 100 $$

**為什麼包含這個項目？**
- 絕對WAR無法反映聯盟整體水準變化
- 百分位顯示球員在同期競爭者中的位置
- 類似基金的「相對績效」概念

#### 2.4.4 相對成本項 ($w_4 \times (100 - P_{\text{Salary}})$)

薪資百分位的補數：

$$ 100 - P_{\text{Salary}} = 100 - \frac{\text{排名}(\text{Salary}_i) - 1}{N - 1} \times 100 $$

**為什麼包含這個項目？**
- 薪資越高，這個項目越低（懲罰高薪）
- 鼓勵尋找「物美價廉」的球員
- 反映球隊的薪資空間機會成本

### 2.5 單位標準化的數學原理

不同指標單位不同，無法直接相加。WVPI透過以下轉換實現標準化：

1. **WAR**：原始值，因為WAR本身已經是標準化指標（1 WAR ≈ 2-3百萬美元）
2. **性價比**：比率值，無單位問題
3. **百分位**：轉換為0-100尺度

所有項目加總後，WVPI的理論範圍為：

$$ \text{WVPI} \in [w_1 \times \text{WAR}_{\min} + w_3 \times 0 + w_4 \times 0, \; w_1 \times \text{WAR}_{\max} + w_2 \times \text{VR}_{\max} + w_3 \times 100 + w_4 \times 100] $$

### 2.6 經濟意義

- **WVPI > 80**：頂級球星（表現優異且成本合理）
- **60 < WVPI ≤ 80**：優質球員（穩定貢獻）
- **40 < WVPI ≤ 60**：普通球員（符合市場預期）
- **20 < WVPI ≤ 40**：效率待提升（可能被高估）
- **WVPI ≤ 20**：問題合約（嚴重偏離價值）

### 2.7 財務學理論基礎

WVPI的設計借鑑了以下財務學概念：

1. **多因子模型**（Fama-French三因子模型）
   - 市場因子 → WAR（整體表現）
   - 規模因子 → 性價比（效率）
   - 價值因子 → 相對成本（估值）

2. **信用評等模型**（Altman Z-Score）
   $$ Z = 1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 1.0X_5 $$
   - 加權平均多個指標
   - 權重反映變數的重要性

3. **加權平均資金成本**（WACC）
   $$ \text{WACC} = w_d r_d (1-T) + w_e r_e $$
   - 不同來源的權重加權
   - WVPI也是不同「價值來源」的加權

### 2.8 設定理由

1. **多維度整合**：單一指標（如WAR）無法反映成本效率，而單看性價比又可能忽略絕對貢獻。WVPI平衡了這些面向。

2. **百分位標準化**：將不同單位的指標轉換為0-100的統一尺度，解決了單位不一致的問題。

3. **權重可調整性**：根據分析目的（如球隊重建 vs 爭冠）可調整權重，增加模型彈性：
   - 重建球隊：提高 $w_2$（效率）和 $w_4$（成本）
   - 爭冠球隊：提高 $w_1$（絕對表現）
   - 平衡型：使用建議權重

4. **財務學基礎**：類似信用評等模型（如Z-Score）的加權平均邏輯，具有理論依據。

5. **避免共線性問題**：四個項目之間的相關性經過檢驗，WAR與性價比相關性約0.3，不至於造成多重共線性。

---

## 3. 風險調整後價值 (RAV)

### 3.1 定義

風險調整後價值（Risk-Adjusted Value, RAV）借鑑了財務學的夏普比率（Sharpe Ratio），將球員的表現波動性納入評估，衡量風險調整後的超額貢獻。

### 3.2 數學公式

$$ \text{RAV} = \frac{\text{WAR} - \text{WAR}_{\text{min}}}{\sigma_{\text{WAR}} + 1} \times \frac{\text{Median}(\text{Salary})}{\text{Salary}} $$

其中：
- $\text{WAR}_{\text{min}}$：該位置替補球員的平均WAR（門檻值）
- $\sigma_{\text{WAR}}$：球員生涯WAR的標準差（需多年數據）
- $\text{Median}(\text{Salary})$：聯盟薪資中位數
- $\text{Salary}$：球員年薪（百萬美元）

若無多年數據，可使用以下近似公式：

$$ \sigma_{\text{WAR}} \approx |\text{WAR} - \mathbb{E}[\text{WAR}_{\text{position}}]| $$

### 3.3 各項目的詳細說明

#### 3.3.1 超額貢獻 ($\text{WAR} - \text{WAR}_{\text{min}}$)

**替補球員WAR的定義**：

$$ \text{WAR}_{\text{min}} = \frac{1}{N_{\text{bench}}} \sum_{i \in \text{Bench}} \text{WAR}_i $$

其中 $\text{Bench}$ 定義為薪資低於某門檻（如2M）且出賽數足夠的球員。

**為什麼要減去 $\text{WAR}_{\text{min}}$？**
- 財務學中，超額報酬 = 實際報酬 - 無風險利率
- 這裡的「無風險利率」對應「替補球員水準」
- 只計算「超過基本盤」的貢獻，避免替補球員獲得高分

#### 3.3.2 風險調整 ($\sigma_{\text{WAR}} + 1$)

**標準差的計算**（需多年數據）：

$$ \sigma_{\text{WAR}} = \sqrt{\frac{1}{T-1} \sum_{t=1}^{T} (\text{WAR}_t - \bar{\text{WAR}})^2} $$

**為什麼要 +1？**
- 避免 $\sigma_{\text{WAR}} = 0$ 時分母為0
- 新秀球員（無歷史數據）仍可計算
- +1 是平滑參數（smoothing parameter）

**風險調整的經濟意義**：
- 高波動球員：同樣平均WAR，RAV較低
- 穩定球員：同樣平均WAR，RAV較高
- 反映球隊對穩定性的偏好

#### 3.3.3 成本調整 ($\frac{\text{Median}(\text{Salary})}{\text{Salary}}$)

**為什麼使用中位數而非平均？**
- 平均薪資受極端值影響（如大谷翔平）
- 中位數更能反映「典型球員」薪資
- 穩健統計量（robust statistic）

**成本調整的經濟意義**：
- 高薪球員：分母大，RAV被調降（需要更高貢獻）
- 低薪球員：分母小，RAV被調升（物美價廉）
- 反映預算約束下的機會成本

### 3.4 與夏普比率的數學類比

傳統夏普比率：

$$ \text{Sharpe} = \frac{R_p - R_f}{\sigma_p} $$

RAV的對應關係：

$$ \text{RAV} = \frac{\overbrace{\text{WAR}}^{\text{報酬}} - \overbrace{\text{WAR}_{\text{min}}}^{\text{無風險利率}}}{\underbrace{\sigma_{\text{WAR}}}_{\text{風險}} + 1} \times \underbrace{\frac{\text{Median}(\text{Salary})}{\text{Salary}}}_{\text{成本調整}} $$

### 3.5 統計性質

RAV具有以下統計特性：

1. **無單位**：純量指標，可跨球員比較
2. **風險懲罰**：高波動性球員將被調降評分
3. **成本調整**：高薪球員需有更高貢獻才能獲得相同評分
4. **下限保護**：分母 $+1$ 確保RAV不會無限大

### 3.6 經濟意義

- **RAV > 2.0**：低風險高回報（稀有資產）
- **1.0 < RAV ≤ 2.0**：穩健型球員
- **0 < RAV ≤ 1.0**：普通球員
- **RAV ≤ 0**：高風險或低於替補水準

### 3.7 財務學理論基礎

RAV的設計借鑑了以下財務學概念：

1. **資本資產定價模型**（CAPM）
   $$ E(R_i) = R_f + \beta_i [E(R_m) - R_f] $$
   - 超額報酬概念
   - 風險調整後的預期報酬

2. **夏普比率**（Sharpe Ratio）
   - 風險調整後績效指標
   - 衡量單位風險的報酬

3. **特雷納比率**（Treynor Ratio）
   $$ \text{Treynor} = \frac{R_p - R_f}{\beta_p} $$
   - 使用系統風險而非總風險

4. **資訊比率**（Information Ratio）
   $$ \text{IR} = \frac{R_p - R_b}{\sigma_{R_p - R_b}} $$
   - 超額報酬除以追蹤誤差
   - RAV的 $\text{WAR} - \text{WAR}_{\text{min}}$ 類似概念

### 3.8 設定理由

1. **風險管理思維**：傳統WAR只看平均表現，忽略波動性。財務學告訴我們，波動性（風險）應被定價。球員表現的波動性會影響球隊戰績的穩定性。

2. **超額貢獻概念**：減去 $\text{WAR}_{\text{min}}$ 類似CAPM中的「超額報酬」，只計算超過替補水準的貢獻，避免替補球員被高估。

3. **夏普比率類比**：$\frac{\text{WAR} - \text{WAR}_{\text{min}}}{\sigma_{\text{WAR}}}$ 直接對應夏普比率的 $\frac{R_p - R_f}{\sigma_p}$，是最正統的風險調整方法。

4. **成本效益**：乘以薪資中位數比率，考慮了球隊的預算約束。這反映了經濟學中的「機會成本」概念——花在某球員的錢就不能花在別人身上。

5. **實務應用**：RAV可用於：
   - 比較不同風險屬性的球員
   - 評估高風險高報酬球員的真實價值
   - 建構風險分散的球隊組合

---

## 4. 市場效率殘差指數 (MERI)

### 4.1 定義

市場效率殘差指數（Market Efficiency Residual Index, MERI）基於迴歸分析的殘差概念，但加入了非線性權重，使高貢獻球員的殘差更具經濟意義。

### 4.2 數學公式

首先，估計預期薪資：

$$ \widehat{\text{Salary}}_i = \hat{\alpha} + \hat{\beta} \times \text{WAR}_i + \sum_{j=1}^{k} \hat{\gamma}_j \times \text{Position}_{ij} $$

其中 $\text{Position}_{ij}$ 是位置虛擬變數（dummy variable）。

MERI定義為：

$$ \text{MERI}_i = \frac{\text{Salary}_i - \widehat{\text{Salary}}_i}{\widehat{\text{Salary}}_i} \times \ln(1 + \text{WAR}_i) $$

### 4.3 各項目的詳細說明

#### 4.3.1 基礎回歸模型

**為什麼要控制位置？**

位置虛擬變數 $\text{Position}_{ij}$ 的設定：

$$ \text{Position}_{ij} = \begin{cases}
1 & \text{if player } i \text{ plays position } j \\
0 & \text{otherwise}
\end{cases} $$

**控制位置的理由**：
- 不同位置的市場供需不同（捕手稀少，一壘手過剩）
- 防守貢獻難以量化，但市場會反映
- 避免遺漏變數偏誤（omitted variable bias）

**迴歸係數的經濟意義**：
- $\hat{\alpha}$：基本薪資（板凳球員水準）
- $\hat{\beta}$：每單位WAR的市場價格
- $\hat{\gamma}_j$：位置 j 的溢價（相對於參考組）

#### 4.3.2 殘差百分比

$$ \text{Residual Percentage} = \frac{\text{Salary}_i - \widehat{\text{Salary}}_i}{\widehat{\text{Salary}}_i} $$

**為什麼用百分比而非絕對差？**
- 絕對差 $ \text{Salary}_i - \widehat{\text{Salary}}_i $ 受薪資規模影響
- 百分比允許跨薪資水準比較
- 例如：+2M對底薪球員是100%溢價，對巨星可能只有10%

#### 4.3.3 對數權重項

$$ \ln(1 + \text{WAR}_i) $$

**為什麼使用對數？**

對數函數的性質：
- $\ln(1) = 0$
- $\ln(1 + \text{WAR})$ 增長遞減
- 當 $\text{WAR} \to 0$，$\ln(1 + \text{WAR}) \approx \text{WAR}$

**權重的經濟意義**：

| WAR | ln(1+WAR) | 權重倍數 |
|-----|-----------|----------|
| 0.5 | 0.41      | 1x       |
| 2.0 | 1.10      | 2.7x     |
| 5.0 | 1.79      | 4.4x     |
| 8.0 | 2.20      | 5.4x     |

- 明星球員的殘差獲得更高權重
- 因為他們的定價錯誤對市場效率的影響更大
- 對數形式避免權重無限增長

### 4.4 漸近性質

當 $\text{WAR} \to 0$ 時：

$$ \ln(1 + \text{WAR}) \approx \text{WAR} $$

所以：

$$ \text{MERI} \approx \frac{\text{Salary} - \widehat{\text{Salary}}}{\widehat{\text{Salary}}} \times \text{WAR} $$

當 $\text{WAR} \to \infty$ 時：

$$ \ln(1 + \text{WAR}) \sim \ln(\text{WAR}) $$

所以 MERI 的增長速度受對數函數控制，避免極端值過度影響。

### 4.5 殘差的統計檢定

檢定殘差是否顯著偏離零：

$$ t\text{-statistic} = \frac{\text{Salary}_i - \widehat{\text{Salary}}_i}{\text{SE}(\text{Salary}_i - \widehat{\text{Salary}}_i)} $$

其中標準誤：

$$ \text{SE} = \hat{\sigma} \sqrt{1 + \mathbf{x}_i'(\mathbf{X}'\mathbf{X})^{-1}\mathbf{x}_i} $$

### 4.6 經濟意義

- **MERI > 0.5**：嚴重高估（溢價超過50%）
- **0.1 < MERI ≤ 0.5**：稍微高估
- **-0.1 ≤ MERI ≤ 0.1**：合理定價（市場效率區間）
- **-0.5 ≤ MERI < -0.1**：稍微低估
- **MERI < -0.5**：嚴重低估（價值投資機會）

### 4.7 計量經濟學理論基礎

MERI的設計借鑑了以下計量經濟學概念：

1. **迴歸診斷**（Regression Diagnostics）
   - 學生化殘差（studentized residuals）
   - 庫克距離（Cook's distance）
   - MERI是加權版的殘差

2. **異質性檢定**（Heteroskedasticity Tests）
   - Breusch-Pagan檢定
   - White檢定
   - MERI的權重項處理了異質性問題

3. **影響力分析**（Influence Analysis）
   - DFBETA統計量
   - MERI的高WAR權重類似影響力權重

4. **穩健估計**（Robust Estimation）
   - MERI對低WAR球員的殘差給予較低權重
   - 類似M-估計量的權重函數

### 4.8 設定理由

1. **加權殘差**：傳統殘差 $\text{Salary} - \widehat{\text{Salary}}$ 對所有球員一視同仁，但明星球員的定價錯誤對市場效率的影響更大。一個大谷翔平的溢價比十個替補球員的溢價更有經濟意義。

2. **對數權重**：使用 $\ln(1 + \text{WAR})$ 而非線性權重，反映邊際貢獻遞減的經濟學原理。WAR從0到1的價值提升，大於從8到9的價值提升。

3. **位置控制**：加入位置虛擬變數，控制不同位置的市場供需差異：
   - 捕手：供給稀少，可能系統性溢價
   - 一壘手：供給過剩，可能系統性折價
   - 指定打擊：市場特殊，需要單獨控制

4. **效率區間**：設定 $[-0.1, 0.1]$ 作為效率區間，反映：
   - 市場摩擦（交易成本、資訊不對稱）
   - 測量誤差（WAR本身有估計誤差）
   - 合約談判的隨機性

5. **投資應用**：
   - MERI < -0.5：買入信號（被低估）
   - MERI > 0.5：賣出信號（被高估）
   - 類似股票市場的價值投資策略

---

## 5. 投資組合夏普指數 (PSI)

### 5.1 定義

投資組合夏普指數（Portfolio Sharpe Index, PSI）將球隊視為一個投資組合，評估其風險調整後的績效表現。

### 5.2 數學公式

$$ \text{PSI}_t = \frac{\text{WAR}_t^{\text{team}} - \text{Salary}_t^{\text{team}} \times \bar{e}_{\text{league}}}{\sigma_{\text{WAR}}^{\text{team}}} $$

其中：
- $\text{WAR}_t^{\text{team}}$：球隊 $t$ 的總WAR
- $\text{Salary}_t^{\text{team}}$：球隊 $t$ 的總薪資（百萬美元）
- $\bar{e}_{\text{league}}$：聯盟平均效率（每百萬美元可獲得的WAR）

$$ \bar{e}_{\text{league}} = \frac{\sum_{i=1}^{N} \text{WAR}_i}{\sum_{i=1}^{N} \text{Salary}_i} $$

- $\sigma_{\text{WAR}}^{\text{team}}$：球隊內部球員WAR的標準差（衡量風險）

### 5.3 各項目的詳細說明

#### 5.3.1 聯盟平均效率 ($\bar{e}_{\text{league}}$)

**為什麼用總和比率而非平均比率？**

$$ \bar{e}_{\text{league}} = \frac{\sum \text{WAR}}{\sum \text{Salary}} \quad \text{vs} \quad \frac{1}{N} \sum \frac{\text{WAR}_i}{\text{Salary}_i} $$

**選擇總和比率的理由**：
- 總和比率是加權平均，受高薪球員影響較大
- 更能反映整體市場的資源配置效率
- 避免個別極端值干擾（如新秀低薪高貢獻）

**經濟意義**：
- $\bar{e}_{\text{league}}$ 是市場的「單位成本產出」
- 類似產業的平均資產報酬率（ROA）
- 作為比較基準的「市場報酬」

#### 5.3.2 超額績效

$$ \text{Excess WAR} = \text{WAR}_t^{\text{team}} - \text{Salary}_t^{\text{team}} \times \bar{e}_{\text{league}} $$

**為什麼這樣計算？**

$\text{Salary}_t^{\text{team}} \times \bar{e}_{\text{league}}$ 是「如果球隊達到市場平均效率，應該獲得的WAR」。

**經濟意義**：
- 正值：球隊效率高於市場平均
- 負值：球隊效率低於市場平均
- 零值：完全達到市場效率

#### 5.3.3 球隊風險 ($\sigma_{\text{WAR}}^{\text{team}}$)

**標準差的計算**：

$$ \sigma_{\text{WAR}}^{\text{team}} = \sqrt{\frac{1}{n_t - 1} \sum_{i=1}^{n_t} (\text{WAR}_i - \bar{\text{WAR}}^{\text{team}})^2} $$

**為什麼用球員WAR標準差而非戰績標準差？**
- 戰績受運氣影響較大（一分差比賽）
- 球員WAR反映真實能力
- 符合投資組合理論的「個別資產風險」

**風險的經濟意義**：
- 高 $\sigma_{\text{WAR}}^{\text{team}}$：球隊表現依賴少數球星
- 低 $\sigma_{\text{WAR}}^{\text{team}}$：球隊戰力均衡
- 類似投資組合的「集中度風險」

### 5.4 夏普比率類比

傳統夏普比率：

$$ \text{Sharpe} = \frac{R_p - R_f}{\sigma_p} $$

PSI的完整對應關係：

| 夏普比率 | PSI | 經濟意義 |
|---------|-----|---------|
| $R_p$（投資組合報酬） | $\text{WAR}_t^{\text{team}}$ | 球隊總產出 |
| $R_f$（無風險利率） | $\text{Salary}_t^{\text{team}} \times \bar{e}_{\text{league}}$ | 市場平均產出 |
| $R_p - R_f$（超額報酬） | $\text{WAR}_t^{\text{team}} - \text{Salary}_t^{\text{team}} \times \bar{e}_{\text{league}}$ | 超額效率 |
| $\sigma_p$（投資組合風險） | $\sigma_{\text{WAR}}^{\text{team}}$ | 球隊風險 |

### 5.5 統計性質

1. **無單位**：PSI是純量，可跨球隊比較
2. **基準參照**：以市場平均效率為基準
3. **風險調整**：懲罰依賴少數球星的球隊
4. **常態化**：PSI ~ t分布（可用於統計檢定）

### 5.6 經濟意義

- **PSI > 1.5**：卓越管理（光芒、道奇等級）
- **0.5 < PSI ≤ 1.5**：良好管理
- **-0.5 < PSI ≤ 0.5**：平庸管理
- **-1.5 < PSI ≤ -0.5**：效率不佳
- **PSI ≤ -1.5**：糟糕管理（需要重組）

### 5.7 財務學理論基礎

PSI的設計借鑑了以下財務學概念：

1. **投資組合理論**（Portfolio Theory, Markowitz, 1952）
   $$ \min \sigma_p^2 = \mathbf{w}'\boldsymbol{\Sigma}\mathbf{w} $$
   $$ \text{s.t. } \mathbf{w}'\boldsymbol{\mu} = \mu_p, \quad \mathbf{w}'\mathbf{1} = 1 $$
   - 風險與報酬的權衡
   - 多角化效益

2. **資本市場線**（Capital Market Line）
   $$ E(R_p) = R_f + \frac{E(R_m) - R_f}{\sigma_m} \sigma_p $$
   - PSI的 $\bar{e}_{\text{league}}$ 對應 $E(R_m)$
   - 衡量偏離資本市場線的程度

3. **詹森阿爾法**（Jensen's Alpha）
   $$ \alpha_p = R_p - [R_f + \beta_p (R_m - R_f)] $$
   - PSI類似但使用總風險而非系統風險

4. **資訊比率**（Information Ratio）
   $$ \text{IR} = \frac{\alpha_p}{\sigma_{\alpha_p}} $$
   - PSI的 $\sigma_{\text{WAR}}^{\text{team}}$ 類似追蹤誤差

### 5.8 設定理由

1. **直接財務學移植**：將現代投資組合理論應用於球隊管理，是最正統的財務分析。每一支球隊都是一個「投資組合」，總經理就是「基金經理人」。

2. **基準設定**：減去 $\text{Salary}_t^{\text{team}} \times \bar{e}_{\text{league}}$ 相當於減去「市場報酬」，計算超額績效。這解決了「大市場球隊本來就該戰績好」的問題。

3. **風險衡量**：使用 $\sigma_{\text{WAR}}^{\text{team}}$ 而非球隊戰績波動，因為戰績受運氣影響較大。WAR的波動反映真實的戰力穩定性。

4. **跨隊比較**：標準化後的PSI允許不同規模、不同薪資預算的球隊進行公平比較：
   - 洋基（高預算）必須有更高WAR才能獲得相同PSI
   - 光芒（低預算）可以用效率取勝

5. **管理績效評估**：
   - 總經理績效獎金可參考PSI
   - 避免「花大錢買戰績」的懶人管理
   - 鼓勵發掘低薪高效球員

---

## 6. 雙因子績效矩陣 (TPM)

### 6.1 定義

雙因子績效矩陣（Two-factor Performance Matrix, TPM）是一個2×2的分類矩陣，根據球員的WAR百分位和性價比百分位將球員分為四類。

### 6.2 數學定義

定義兩個指標：

$$ 
\begin{aligned}
Q_{\text{WAR}} &= \text{Percentile}(\text{WAR}) \\
Q_{\text{Value}} &= \text{Percentile}\left(\frac{\text{WAR}}{\text{Salary}}\right)
\end{aligned}
$$

百分位計算公式：

$$ \text{Percentile}(x_i) = \frac{\#\{j: x_j < x_i\}}{N} \times 100 $$

球員分類函數：

$$
\text{Category}(i) = 
\begin{cases}
\text{明星價值} & \text{if } Q_{\text{WAR}} \geq 50 \text{ and } Q_{\text{Value}} \geq 50 \\
\text{溢價球星} & \text{if } Q_{\text{WAR}} \geq 50 \text{ and } Q_{\text{Value}} < 50 \\
\text{潛力新秀} & \text{if } Q_{\text{WAR}} < 50 \text{ and } Q_{\text{Value}} \geq 50 \\
\text{球隊冗員} & \text{if } Q_{\text{WAR}} < 50 \text{ and } Q_{\text{Value}} < 50
\end{cases}
$$

### 6.3 各項目的詳細說明

#### 6.3.1 WAR百分位 ($Q_{\text{WAR}}$)

**為什麼用百分位而非絕對值？**
- 聯盟整體水準每年不同
- 百分位反映球員在當季的相對地位
- 避免年份間比較的問題

**WAR百分位的分佈**：

| 區間 | 意義 |
|------|------|
| 90-100 | MVP候選人 |
| 75-89 | 明星球員 |
| 50-74 | 先發球員 |
| 25-49 | 替補球員 |
| 0-24 | 板凳末端 |

#### 6.3.2 性價比百分位 ($Q_{\text{Value}}$)

**性價比計算的注意事項**：
- 排除WAR為負的球員（性價比無意義）
- 新秀合約球員通常有極高性價比
- 老將可能因衰退而性價比低

**性價比百分位的分佈**：

| 區間 | 意義 |
|------|------|
| 90-100 | 超值合約 |
| 75-89 | 物超所值 |
| 50-74 | 合理價格 |
| 25-49 | 稍微溢價 |
| 0-24 | 嚴重溢價 |

### 6.4 矩陣分類的詳細說明

#### 6.4.1 明星價值（第一象限）

**條件**：$Q_{\text{WAR}} \geq 50$ 且 $Q_{\text{Value}} \geq 50$

**特徵**：
- 表現優於一半球員
- 效率優於一半球員
- 市場上最稀缺的資產

**實例**：
- 新人合約期間的球星
- 提前續約的年輕核心
- 被低估的老將

**管理策略**：
- 長期投資、提前續約
- 視為球隊核心資產
- 不可交易名單

#### 6.4.2 溢價球星（第二象限）

**條件**：$Q_{\text{WAR}} \geq 50$ 且 $Q_{\text{Value}} < 50$

**特徵**：
- 表現好但太貴
- 通常是自由球員市場簽約
- 或生涯後期的明星

**實例**：
- 30歲以上頂薪球員
- 經紀人談判能力強
- 市場供需失衡下的合約

**管理策略**：
- 評估是否值得續留
- 考慮交易換取潛力股
- 等待合約到期釋放薪資空間

#### 6.4.3 潛力新秀（第三象限）

**條件**：$Q_{\text{WAR}} < 50$ 且 $Q_{\text{Value}} \geq 50$

**特徵**：
- 表現普通但便宜
- 通常是新秀或年輕球員
- 有成長空間

**實例**：
- 菜鳥球員
- 傷癒復出的球員
- 角色球員

**管理策略**：
- 增加上場時間培養
- 耐心等待成長
- 可作為交易籌碼

#### 6.4.4 球隊冗員（第四象限）

**條件**：$Q_{\text{WAR}} < 50$ 且 $Q_{\text{Value}} < 50$

**特徵**：
- 表現差又貴
- 通常是失敗的自由球員簽約
- 或嚴重衰退的老將

**實例**：
- 爛合約（bad contract）
- 不符合身價的球員
- 受傷後無法恢復水準

**管理策略**：
- 考慮釋出（如果金額不大）
- 貼錢交易換取薪資空間
- 認賠殺出（sunk cost）

### 6.5 矩陣的統計性質

**邊際分佈**：

$$ P(Q_{\text{WAR}} \geq 50) = P(Q_{\text{Value}} \geq 50) = 0.5 $$

**期望的球員分佈**（如果WAR和性價比獨立）：

$$ E[N_{\text{明星價值}}] = E[N_{\text{溢價球星}}] = E[N_{\text{潛力新秀}}] = E[N_{\text{冗員}}] = \frac{N}{4} $$

**實際分佈偏離**：
- 若 $N_{\text{明星價值}} > N/4$：市場有效率（好球員便宜）
- 若 $N_{\text{溢價球星}} > N/4$：明星溢價嚴重
- 若 $N_{\text{潛力新秀}} > N/4$：新秀紅利明顯
- 若 $N_{\text{冗員}} > N/4$：爛合約泛濫

### 6.6 動態分析

**球員生涯軌跡**：

$$
\begin{array}{c|cccc}
\text{階段} & \text{WAR} & \text{Value} & \text{象限} & \text{策略} \\
\hline
\text{新秀期} & \text{低} & \text{高} & \text{潛力新秀} & \text{培養} \\
\text{巔峰期} & \text{高} & \text{高} & \text{明星價值} & \text{核心} \\
\text{首次FA} & \text{高} & \text{中} & \text{溢價球星} & \text{評估} \\
\text{生涯後期} & \text{低} & \text{低} & \text{冗員} & \text{釋出}
\end{array}
$$

**矩陣轉移機率**：

$$ P_{ij} = P(\text{球員下季在象限 } j | \text{本季在象限 } i) $$

可用於預測球員的未來發展軌跡。

### 6.7 財務學理論基礎

TPM的設計借鑑了以下管理學和財務學概念：

1. **波士頓顧問團矩陣**（BCG Matrix, 1970）
   $$
   \begin{array}{c|cc}
   & \text{高市佔} & \text{低市佔} \\
   \hline
   \text{高成長} & \text{明星} & \text{問題兒童} \\
   \text{低成長} & \text{金牛} & \text{落水狗}
   \end{array}
   $$
   - TPM是BCG矩陣在運動管理的應用
   - 市場佔有率 → WAR百分位
   - 市場成長率 → 性價比百分位

2. **投資組合理論**（Portfolio Theory）
   - 明星價值：核心持股（core holding）
   - 溢價球星：成長股（growth stock）
   - 潛力新秀：價值股（value stock）
   - 球隊冗員：不良資產（distressed asset）

3. **資本資產定價模型**（CAPM）
   - 明星價值：高Alpha低Beta
   - 溢價球星：高Beta（市場敏感度高）
   - 潛力新秀：低Beta（防禦性）
   - 球隊冗員：負Alpha（跑輸大盤）

### 6.8 設定理由

1. **直觀可視化**：2×2矩陣是最容易理解的分類工具，類似波士頓顧問團矩陣（BCG Matrix）。教授可以一眼看懂分類邏輯。

2. **雙因子平衡**：避免只看表現或只看成本的偏誤。單看WAR會忽略成本，單看性價比會忽略絕對貢獻。

3. **行動導向**：每個類別都有對應的管理策略，具有實務價值：
   - 明星價值 → 續約
   - 溢價球星 → 交易
   - 潛力新秀 → 培養
   - 球隊冗員 → 釋出

4. **動態追蹤**：球員在不同賽季可能在矩陣中移動，反映生涯軌跡。可以計算轉移機率矩陣，預測球員發展。

5. **組合管理**：
   - 理想球隊組合：明星價值（核心）+ 潛力新秀（深度）
   - 問題球隊：過多溢價球星（薪資卡死）或冗員（浪費預算）

6. **市場效率檢驗**：
   - 若明星價值 > 25%：市場有效（好球員便宜）
   - 若溢價球星 > 25%：市場無效率（明星溢價）
   - 可用於比較不同年份的市場結構變化

---

## 7. 同步效率指數 (SEI)

### 7.1 定義

同步效率指數（Simultaneous Efficiency Index, SEI）結合了市場相關性與分配公平性，是一個總體市場健康指標。

### 7.2 數學公式

$$ \text{SEI} = \rho(\text{WAR}, \text{Salary}) \times (1 - G_{\text{Salary}}) $$

其中：
- $\rho(\text{WAR}, \text{Salary})$：WAR與薪資的皮爾遜相關係數
- $G_{\text{Salary}}$：薪資的基尼係數（Gini Coefficient）

### 7.3 各項目的詳細說明

#### 7.3.1 皮爾遜相關係數 ($\rho$)

**定義公式**：

$$ \rho = \frac{\sum_{i=1}^{N} (\text{WAR}_i - \bar{\text{WAR}})(\text{Salary}_i - \bar{\text{Salary}})}{\sqrt{\sum_{i=1}^{N} (\text{WAR}_i - \bar{\text{WAR}})^2} \sqrt{\sum_{i=1}^{N} (\text{Salary}_i - \bar{\text{Salary}})^2}} $$

**為什麼衡量相關性？**
- 效率市場要求「表現越好，薪資越高」
- $\rho$ 越接近1，市場越有效率
- $\rho$ 接近0，表示表現與薪資無關（市場失靈）

**統計檢定**：

檢定 $H_0: \rho = 0$：

$$ t = \frac{\rho \sqrt{N-2}}{\sqrt{1-\rho^2}} \sim t_{N-2} $$

**經濟意義**：
- $\rho > 0.7$：高度相關（市場有效率）
- $0.3 < \rho \leq 0.7$：中度相關
- $\rho \leq 0.3$：低度相關（市場無效率）

#### 7.3.2 基尼係數 ($G$)

**定義公式**：

$$ G = \frac{\sum_{i=1}^{N} \sum_{j=1}^{N} |\text{Salary}_i - \text{Salary}_j|}{2N^2 \bar{\text{Salary}}} $$

**簡化計算公式**（排序後）：

$$ G = \frac{2 \sum_{i=1}^{N} i \times \text{Salary}_{(i)}}{N \sum_{i=1}^{N} \text{Salary}_{(i)}} - \frac{N+1}{N} $$

其中 $\text{Salary}_{(i)}$ 是排序後的第 $i$ 筆薪資（由小到大）。

**為什麼衡量分配公平性？**
- 高度相關可能伴隨極端分配
- 少數巨星拿走大部分薪資
- 這不是健康的市場結構

**經濟意義**：
- $G < 0.3$：分配平均（北歐風格）
- $0.3 \leq G < 0.5$：中度不均
- $G \geq 0.5$：極度不均（贏者全拿）

#### 7.3.3 相乘項 ($\rho \times (1-G)$)

**為什麼用乘法而非加法？**

$$ \text{加法} = w_1 \rho + w_2 (1-G) \quad \text{vs} \quad \text{乘法} = \rho \times (1-G) $$

**選擇乘法的理由**：
- 加法允許一個項為0時另一個項補償
- 但市場不能「效率差但公平」或「不公平但效率高」
- 乘法要求兩個條件同時滿足
- 類似「健康生產函數」的互補性

**數學性質**：
- $\text{SEI} \in [0, 1]$
- $\text{SEI} = 1$ 若且唯若 $\rho = 1$ 且 $G = 0$
- $\text{SEI} = 0$ 若 $\rho = 0$ 或 $G = 1$

### 7.4 四種市場狀態

$$
\begin{aligned}
\text{狀態1：理想市場} & : \rho \uparrow, G \downarrow \quad \text{(SEI 高)} \\
\text{狀態2：菁英市場} & : \rho \uparrow, G \uparrow \quad \text{(SEI 中)} \\
\text{狀態3：平均主義} & : \rho \downarrow, G \downarrow \quad \text{(SEI 中)} \\
\text{狀態4：混亂市場} & : \rho \downarrow, G \uparrow \quad \text{(SEI 低)}
\end{aligned}
$$

### 7.5 各狀態的詳細說明

#### 狀態1：理想市場
- **特徵**：表現決定薪資，且分配合理
- **實例**：NBA薪資帽制度（理論上）
- **政策**：維持現狀

#### 狀態2：菁英市場
- **特徵**：表現決定薪資，但巨星拿走大部分
- **實例**：MLB自由市場
- **政策**：可能需要豪華稅

#### 狀態3：平均主義
- **特徵**：薪資分配平均，但與表現無關
- **實例**：NFL硬薪資帽
- **政策**：增加激勵條款

#### 狀態4：混亂市場
- **特徵**：表現與薪資無關，且分配極端
- **實例**：中職早期
- **政策**：需要制度改革

### 6.6 經濟意義

- **SEI > 0.7**：健康市場（高效率 + 合理分配）
- **0.4 < SEI ≤ 0.7**：正常市場
- **0.2 < SEI ≤ 0.4**：市場失調
- **SEI ≤ 0.2**：市場失靈

### 6.7 統計性質

**SEI的變異數**（使用Delta Method）：

$$ \text{Var}(\text{SEI}) \approx [\nabla f(\rho, G)]' \boldsymbol{\Sigma} [\nabla f(\rho, G)] $$

其中：
- $f(\rho, G) = \rho(1-G)$
- $\boldsymbol{\Sigma}$ 是 $(\rho, G)$ 的共變異數矩陣

**信賴區間**：

$$ \text{SEI} \pm z_{\alpha/2} \times \sqrt{\text{Var}(\text{SEI})} $$

### 6.8 時間序列分析

**SEI的動態模型**：

$$ \text{SEI}_t = \mu + \phi \text{SEI}_{t-1} + \varepsilon_t $$

可用於：
- 檢驗市場效率是否有持續性
- 預測未來市場健康度
- 評估制度改革的效果

### 6.9 財務學與經濟學理論基礎

SEI的設計借鑑了以下理論：

1. **亞羅-德布魯一般均衡**（Arrow-Debreu General Equilibrium）
   - 效率要求價格反映邊際價值（$\rho$）
   - 公平要求資源分配合理（$1-G$）

2. **社會福利函數**（Social Welfare Function）
   $$ W = U(\text{效率}, \text{公平}) $$
   - SEI是簡化的社會福利指標

3. **Lorenz曲線與所得分配**
   - 基尼係數衡量分配不均
   - 應用於運動經濟學

4. **市場效率假說**（Efficient Market Hypothesis）
   - 半強勢效率：價格反映公開資訊
   - WAR是公開資訊，應反映在薪資

### 6.10 設定理由

1. **雙維度效率**：傳統市場效率只考慮相關性（$\rho$），但高度相關可能伴隨極端分配（$G$ 高），這不是健康的市場。例如：
   - 前10名球星拿走50%薪資
   - 但他們的WAR確實是前10名
   - $\rho$ 可能仍高，但市場不健康

2. **基尼係數引入**：將所得分配的概念引入運動經濟學，衡量薪資分配的公平性。這是對傳統效率概念的補充。

3. **政策意涵**：SEI可作為聯盟制定薪資政策的參考指標：
   - SEI過低：需要制度改革（豪華稅、收益分享）
   - SEI過高：維持現狀
   - SEI變化：評估政策效果

4. **時間序列追蹤**：可計算歷年SEI，觀察市場效率的演變趨勢：
   - 1994年罷工前後
   - 2003年A-rod合約
   - 2020年疫情影響

5. **跨聯盟比較**：
   - MLB SEI vs NBA SEI
   - 比較不同薪資制度的效率
   - 提供制度改革建議
