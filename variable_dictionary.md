# MLB 專題變數定義與公式說明(按ctrl+shift+v)

## 數據來源與工具

### 數據獲取工具
- **pybaseball**: Python套件，用於獲取MLB官方統計數據
- **數據年限**: 2023年賽季
- **資格限制**: 
  - 打者: 至少50個打席 (qual=50)
  - 投手: 至少30局投球 (qual=30)

##  打者表現指標

### 基礎傳統指標
| 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 |
|--------|----------|----------|--------------|
| **Name** | Player Name | 球員姓名 | - |
| **Team** | Team | 所屬球隊 | - |
| **W** | Wins | 勝場數 | 球員所屬球隊在該球員出賽時的勝場數 |
| **L** | Losses | 敗場數 | 球員所屬球隊在該球員出賽時的敗場數 |
| **W-L%** | Win-Loss Percentage | 勝率 | W / (W + L) |
| **GB** | Games Behind | 勝差 | 與分區領先球隊的勝場差 |

### 打擊表現指標
| 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 |
|--------|----------|----------|--------------|
| **PA** | Plate Appearances | 打席數 | 上場打擊的次數 |
| **AB** | At Bats | 打數 | 打席數扣除保送、犧牲打等 |
| **R** | Runs | 得分 | 跑回本壘得分 |
| **H** | Hits | 安打數 | - |
| **2B** | Doubles | 二壘安打 | - |
| **3B** | Triples | 三壘安打 | - |
| **HR** | Home Runs | 全壘打 | - |
| **RBI** | Runs Batted In | 打點 | 使跑者得分 |
| **SB** | Stolen Bases | 盜壘成功 | - |
| **CS** | Caught Stealing | 盜壘失敗 | - |

### 進階打擊率指標
| 變數名 | 英文全名 | 中文名稱 | 計算公式 | 說明 |
|--------|----------|----------|----------|------|
| **AVG** | Batting Average | 打擊率 | H / AB | 衡量擊出安打的能力 |
| **OBP** | On-Base Percentage | 上壘率 | (H + BB + HBP) / (AB + BB + HBP + SF) | 衡量上壘能力 |
| **SLG** | Slugging Percentage | 長打率 | (1B + 2×2B + 3×3B + 4×HR) / AB | 衡量長打能力 |
| **OPS** | On-base Plus Slugging | 綜合攻擊指數 | OBP + SLG | 綜合評估攻擊能力 |

### 進階分析指標
| 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 | 
|--------|----------|----------|--------------|
| **WAR** | Wins Above Replacement | 勝場貢獻值 | **最重要指標**<br>衡量球員比替補球員多貢獻多少勝場 | 
| **wOBA** | Weighted On-Base Average | 加權上壘率 | 考慮不同上壘方式的價值 | 
| **wRC+** | Weighted Runs Created Plus | 調整後得分創造 | 100為聯盟平均，>100優於平均 | 
| **OPS+** | Adjusted OPS | 調整後OPS | 考慮球場因素，100為聯盟平均 | 

## 投手表現指標

### 基礎投球數據
| 變數名 | 英文全名 | 中文名稱 | 說明 |
|--------|----------|----------|------|
| **W** | Wins | 勝投 | 先發投手投滿5局且球隊領先時退場 |
| **L** | Losses | 敗投 | 失分導致球隊落後時退場 |
| **ERA** | Earned Run Average | 防禦率 | 每9局自責分，越低越好 |
| **G** | Games | 出賽數 | - |
| **GS** | Games Started | 先發場次 | - |
| **CG** | Complete Games | 完投 | 投完整場比賽 |
| **SHO** | Shutouts | 完封 | 完投且對方未得分 |

### 投球結果數據
| 變數名 | 英文全名 | 中文名稱 | 計算公式 |
|--------|----------|----------|----------|
| **IP** | Innings Pitched | 投球局數 | 如 202.1 表示202又1/3局 |
| **H** | Hits Allowed | 被安打數 | - |
| **R** | Runs Allowed | 失分 | - |
| **ER** | Earned Runs | 自責分 | 扣除隊友失誤導致的失分 |
| **HR** | Home Runs Allowed | 被全壘打數 | - |
| **BB** | Walks | 保送 | - |
| **SO** | Strikeouts | 三振 | - |

### 進階投球指標
| 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 |
|--------|----------|----------|--------------|
| **WAR** | Wins Above Replacement | 勝場貢獻值 | 投手版，衡量對球隊勝場貢獻 |
| **WHIP** | Walks and Hits per Inning | 每局被上壘率 | (BB + H) / IP |
| **FIP** | Fielding Independent Pitching | 防守獨立投球指數 | 只考慮三振、保送、全壘打的防禦率 |
| **xFIP** | Expected FIP | 預期FIP | 考慮被擊球品質調整的FIP |

## 薪資相關變數（模擬/真實）

### 模擬薪資變數（當前使用）
| 變數名 | 說明 | 計算公式 |
|--------|------|----------|
| **simulated_salary** | 模擬薪資（美元） | `base_salary + WAR × war_value + random_error` |
| **salary_in_millions** | 薪資（百萬美元） | `simulated_salary / 1,000,000` |
| **value_ratio** | 性價比 | `WAR / salary_in_millions` |

### 模擬參數設定
```python
base_salary = 600000      # 底薪：MLB最低薪資
war_value = 8500000       # 每WAR價值：850萬美元
random_error = np.random.normal(0, 2000000, n)  # 隨機誤差：±200萬