# dashboard.py - MLB薪資表現分析儀表板（優化整合版）
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from scipy import stats  # 新增：用於計算百分位數和統計分佈

# ============================================================
# 設定頁面配置
# ============================================================
st.set_page_config(
    page_title="MLB薪資表現分析儀表板",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 自定義CSS樣式
# ============================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    .section-title {
        font-size: 1.8rem;
        color: #3B82F6;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-box {
        background-color: #f0f9ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 20px;
    }
    .formula-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #10B981;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 標題區域
# ============================================================
st.markdown('<h1 class="main-title">⚾ MLB球員薪資與表現分析儀表板</h1>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">
    <p style="font-size: 1.1rem;">計量經濟學與財務分析專題：檢驗MLB薪資市場效率性</p>
    <p style="font-size: 0.9rem;">最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 數據載入函數
# ============================================================
@st.cache_data(ttl=3600)
@st.cache_data(ttl=3600)
def load_data():
    """從雲端資料夾載入數據"""
    try:
        # 獲取當前程式所在的目錄
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 可能的數據檔案路徑列表（依優先順序）
        possible_paths = [
            os.path.join(current_dir, "data", "merged_performance_salary.csv"),
            os.path.join(current_dir, "data", "processed", "merged_performance_salary.csv"),
            os.path.join(current_dir, "merged_performance_salary.csv"),
            os.path.join(current_dir, "mlb_salaries_2024", "data", "merged_performance_salary.csv"),
            os.path.join(os.path.dirname(current_dir), "data", "merged_performance_salary.csv")
        ]
        
        # 嘗試每個路徑
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                st.write(f"✅ 找到數據檔案: {data_path}")
                break
        
        # 如果都找不到
        if data_path is None:
            st.error("❌ 找不到數據檔案")
            st.write("請確認你的 GitHub 倉庫中有以下其中一個檔案：")
            st.write("1. `data/merged_performance_salary.csv`")
            st.write("2. `data/processed/merged_performance_salary.csv`")
            st.write("3. `merged_performance_salary.csv`")
            
            # 顯示當前目錄結構（幫助除錯）
            st.write("---")
            st.write("📂 當前目錄結構：")
            try:
                files = os.listdir(current_dir)
                st.write(f"根目錄: {files}")
                if 'data' in files:
                    data_files = os.listdir(os.path.join(current_dir, 'data'))
                    st.write(f"data/ 目錄: {data_files}")
            except:
                pass
            
            return None
        
        # 讀取數據
        df = pd.read_csv(data_path)
        st.success(f"✅ 成功載入 {len(df)} 筆數據")

        # 數據預處理
        if 'value_ratio' not in df.columns and 'WAR' in df.columns and 'Salary_millions' in df.columns:
            df['value_ratio'] = df['WAR'] / df['Salary_millions']
        
        # 標準化欄位名稱
        column_mapping = {}
        
        if 'Team' not in df.columns:
            possible_team_cols = ['Team_performance', 'Team_salary', 'team', 'TEAM']
            for col in possible_team_cols:
                if col in df.columns:
                    column_mapping[col] = 'Team'
                    break
        
        if 'Position' not in df.columns:
            possible_pos_cols = ['Position_salary', 'position', 'Pos', 'POS']
            for col in possible_pos_cols:
                if col in df.columns:
                    column_mapping[col] = 'Position'
                    break
        
        if 'Name' not in df.columns:
            possible_name_cols = ['Name_clean', 'Player', 'Player_formatted', 'player']
            for col in possible_name_cols:
                if col in df.columns:
                    column_mapping[col] = 'Name'
                    break
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            
        if 'Team' in df.columns:
            df = df[df['Team'] != '---']
            df = df.dropna(subset=['Team'])
            df['Team'] = df['Team'].astype(str)
            
        pos_map = {
            1: 'P', '1': 'P', '1.0': 'P',
            2: 'C', '2': 'C', '2.0': 'C',
            3: '1B', '3': '1B', '3.0': '1B',
            4: '2B', '4': '2B', '4.0': '2B',
            5: '3B', '5': '3B', '5.0': '3B',
            6: 'SS', '6': 'SS', '6.0': 'SS',
            7: 'LF', '7': 'LF', '7.0': 'LF',
            8: 'CF', '8': 'CF', '8.0': 'CF',
            9: 'RF', '9': 'RF', '9.0': 'RF',
            10: 'DH', '10': 'DH', 'O': 'DH'
        }

        if 'Position' in df.columns:
            df['Position'] = df['Position'].apply(lambda x: pos_map.get(x, x))

        # 計算財務分析指標
        if 'Salary_millions' in df.columns:
            df['salary_percentile'] = df['Salary_millions'].rank(pct=True) * 100
            df['salary_category'] = pd.qcut(df['Salary_millions'], q=4, 
                                            labels=['低薪資', '中低薪資', '中高薪資', '高薪資'])
        
        if 'WAR' in df.columns:
            df['war_percentile'] = df['WAR'].rank(pct=True) * 100
            df['war_category'] = pd.qcut(df['WAR'], q=4,
                                        labels=['低表現', '中低表現', '中高表現', '高表現'])
        
        # ============================================================
        # 新增：計算原創財務指標 (依據 new_variables.md)
        # ============================================================
        df = calculate_original_financial_metrics(df)
        
        # 除錯：檢查 WVPI 分佈
        debug_wvpi(df)
        
        return df
    
    except Exception as e:
        st.error(f"❌ 讀取數據失敗: {e}")
        return None

# 將 debug_wvpi 函數移到 load_data 函數之後
def debug_wvpi(df):
    """檢查 WVPI 的實際分佈"""
    if 'WVPI' in df.columns:
        print("=" * 50)
        print("WVPI 統計摘要:")
        print(f"最小值: {df['WVPI'].min():.2f}")
        print(f"最大值: {df['WVPI'].max():.2f}")
        print(f"平均值: {df['WVPI'].mean():.2f}")
        print(f"中位數: {df['WVPI'].median():.2f}")
        print(f"標準差: {df['WVPI'].std():.2f}")
        print("\n百分位數:")
        for p in [10, 25, 50, 75, 90, 95, 99]:
            print(f"{p}th: {df['WVPI'].quantile(p/100):.2f}")
        print("=" * 50)

# ============================================================
# 新增：原創財務指標計算函數 (依據 new_variables.md)
# ============================================================
def calculate_original_financial_metrics(df):
    """計算六個原創財務指標：WVPI, RAV, MERI, PSI, TPM, SEI"""
    
    # 檢查必要欄位
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        st.warning("⚠️ 缺少 WAR 或 Salary_millions 欄位，無法計算部分原創指標")
        return df
    
    # 2. 加權綜合價值指數 (WVPI)
    df = calculate_wvpi(df)
    
    # 3. 風險調整後價值 (RAV)
    df = calculate_rav(df)
    
    # 4. 市場效率殘差指數 (MERI)
    df = calculate_meri(df)
    
    # 5. 投資組合夏普指數 (PSI) - 需要球隊層級計算，稍後在球隊分析中進行
    
    # 6. 雙因子績效矩陣 (TPM) - 需要百分位，已在計算中
    
    # 7. 同步效率指數 (SEI) - 需要全局計算，稍後在綜合儀表板中進行
    
    return df

def calculate_wvpi(df):
    """計算加權綜合價值指數 (WVPI) - 修正版（所有項目標準化到 0-100）"""
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        return df
    
    # 定義權重 (依據 new_variables.md 2.3 節)
    w1, w2, w3, w4 = 0.35, 0.30, 0.20, 0.15
    
    # 計算 WAR 百分位
    df['P_WAR'] = df['WAR'].rank(pct=True) * 100
    
    # 計算薪資百分位
    df['P_Salary'] = df['Salary_millions'].rank(pct=True) * 100
    
    # 計算 100 - P_Salary (相對成本項)
    df['P_Salary_inv'] = 100 - df['P_Salary']
    
    # 計算性價比 (WAR/Salary)
    df['VR'] = df['WAR'] / df['Salary_millions']
    
    # ==== 新增：標準化 WAR 和 VR 到 0-100 尺度 ====
    war_max = df['WAR'].max()
    vr_max = df['VR'].max()
    
    # 標準化 WAR (避免除以零)
    if war_max > 0:
        df['WAR_norm'] = (df['WAR'] / war_max) * 100
    else:
        df['WAR_norm'] = 0
    
    # 標準化 VR (避免除以零)
    if vr_max > 0:
        df['VR_norm'] = (df['VR'] / vr_max) * 100
    else:
        df['VR_norm'] = 0
    
    # 計算 WVPI - 使用標準化後的數值
    df['WVPI'] = (w1 * df['WAR_norm'] + 
                  w2 * df['VR_norm'] + 
                  w3 * df['P_WAR'] + 
                  w4 * df['P_Salary_inv'])
    
    # ==== 修正：根據實際分佈調整分類閾值 ====
    # 先計算 WVPI 的百分位數，用於調整整體分佈
    p25 = df['WVPI'].quantile(0.25)
    p50 = df['WVPI'].quantile(0.50)
    p75 = df['WVPI'].quantile(0.75)
    p90 = df['WVPI'].quantile(0.90)
    p95 = df['WVPI'].quantile(0.95)
    
    # 根據實際分佈設定閾值
    conditions = [
        df['WVPI'] > p90,                          # 前10% -> 頂級球星
        (df['WVPI'] > p75) & (df['WVPI'] <= p90),  # 前10-25% -> 優質球員
        (df['WVPI'] > p50) & (df['WVPI'] <= p75),  # 前25-50% -> 普通球員
        (df['WVPI'] > p25) & (df['WVPI'] <= p50),  # 後25-50% -> 效率待提升
        df['WVPI'] <= p25                           # 後25% -> 問題合約
    ]
    categories = ['頂級球星', '優質球員', '普通球員', '效率待提升', '問題合約']
    df['WVPI_category'] = np.select(conditions, categories, default='未知')
    
    return df

def calculate_rav(df):
    """計算風險調整後價值 (RAV)"""
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        return df
    
    # 計算 WAR_min (替補球員水準) - 使用薪資低於第25百分位的球員平均WAR
    low_salary_threshold = df['Salary_millions'].quantile(0.25)
    bench_players = df[df['Salary_millions'] <= low_salary_threshold]
    WAR_min = bench_players['WAR'].mean() if len(bench_players) > 0 else 0
    
    # 計算 σ_WAR (生涯WAR標準差) - 由於無多年數據，使用近似公式
    # 使用位置平均WAR的絕對差異作為近似
    if 'Position' in df.columns:
        position_avg_war = df.groupby('Position')['WAR'].transform('mean')
        df['sigma_WAR_approx'] = np.abs(df['WAR'] - position_avg_war)
    else:
        df['sigma_WAR_approx'] = df['WAR'].std() if df['WAR'].std() > 0 else 1
    
    # 計算薪資中位數
    median_salary = df['Salary_millions'].median()
    
    # 計算 RAV
    df['RAV'] = ((df['WAR'] - WAR_min) / (df['sigma_WAR_approx'] + 1)) * (median_salary / df['Salary_millions'])
    
    # 添加 RAV 分類 (依據 new_variables.md 3.6 節)
    conditions = [
        df['RAV'] > 2.0,
        (df['RAV'] > 1.0) & (df['RAV'] <= 2.0),
        (df['RAV'] > 0) & (df['RAV'] <= 1.0),
        df['RAV'] <= 0
    ]
    categories = ['低風險高回報', '穩健型球員', '普通球員', '高風險或低於替補']
    df['RAV_category'] = np.select(conditions, categories, default='未知')
    
    return df

def calculate_meri(df):
    """計算市場效率殘差指數 (MERI)"""
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        return df
    
    # 清理數據
    df_clean = df.dropna(subset=['WAR', 'Salary_millions']).copy()
    
    # 建立線性回歸模型 (WAR -> Salary)
    X = df_clean[['WAR']].values
    y = df_clean['Salary_millions'].values
    
    # 簡單線性回歸 (不使用外部庫)
    X_mean = np.mean(X)
    y_mean = np.mean(y)
    
    numerator = np.sum((X.flatten() - X_mean) * (y - y_mean))
    denominator = np.sum((X.flatten() - X_mean) ** 2)
    
    beta = numerator / denominator if denominator != 0 else 0
    alpha = y_mean - beta * X_mean
    
    # 計算預期薪資
    df['expected_salary'] = alpha + beta * df['WAR']
    
    # 如果位置數據存在，加入位置調整 (簡化版)
    if 'Position' in df.columns:
        position_avg_residual = df.groupby('Position')['Salary_millions'].transform('mean') - \
                                df.groupby('Position')['expected_salary'].transform('mean')
        df['expected_salary_position'] = df['expected_salary'] + position_avg_residual
    else:
        df['expected_salary_position'] = df['expected_salary']
    
    # 計算殘差百分比
    df['residual_pct'] = (df['Salary_millions'] - df['expected_salary_position']) / df['expected_salary_position']
    
    # 計算 MERI = 殘差百分比 × ln(1 + WAR)
    df['MERI'] = df['residual_pct'] * np.log(1 + np.abs(df['WAR']))
    
    # 添加 MERI 分類 (依據 new_variables.md 4.6 節)
    conditions = [
        df['MERI'] > 0.5,
        (df['MERI'] > 0.1) & (df['MERI'] <= 0.5),
        (df['MERI'] >= -0.1) & (df['MERI'] <= 0.1),
        (df['MERI'] >= -0.5) & (df['MERI'] < -0.1),
        df['MERI'] < -0.5
    ]
    categories = ['嚴重高估', '稍微高估', '合理定價', '稍微低估', '嚴重低估']
    df['MERI_category'] = np.select(conditions, categories, default='未知')
    
    return df

def calculate_team_psi(team_df, league_efficiency):
    """計算單一球隊的投資組合夏普指數 (PSI)"""
    total_war = team_df['WAR'].sum()
    total_salary = team_df['Salary_millions'].sum()
    expected_war = total_salary * league_efficiency
    excess_war = total_war - expected_war
    team_risk = team_df['WAR'].std() if len(team_df) > 1 else 1
    
    # PSI = 超額WAR / 球隊風險
    psi = excess_war / team_risk if team_risk != 0 else 0
    return psi

def calculate_sei(df):
    """計算同步效率指數 (SEI)"""
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        return 0, 0, 0
    
    # 計算 WAR 與薪資的相關係數
    df_clean = df.dropna(subset=['WAR', 'Salary_millions'])
    correlation = df_clean['WAR'].corr(df_clean['Salary_millions'])
    
    # 計算薪資的基尼係數
    salaries = df_clean['Salary_millions'].values
    salaries = salaries[salaries > 0]
    
    if len(salaries) > 0:
        # 計算基尼係數
        salaries_sorted = np.sort(salaries)
        n = len(salaries_sorted)
        index = np.arange(1, n + 1)
        gini = ((2 * index - n - 1) * salaries_sorted).sum() / (n * salaries_sorted.sum())
    else:
        gini = 0
    
    # SEI = ρ × (1 - G)
    sei = correlation * (1 - gini)
    
    return correlation, gini, sei

# ============================================================
# 輔助函數 (含新增的高階分析函數)
# ============================================================
def calculate_regression(x, y):
    """計算線性回歸的替代方法（不使用statsmodels）"""
    try:
        A = np.vstack([x, np.ones(len(x))]).T
        slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
        
        y_pred = slope * x + intercept
        residuals = y - y_pred
        
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        correlation = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0
        
        return slope, intercept, correlation, r_squared
    except Exception as e:
        st.warning(f"回歸計算發生錯誤: {e}")
        return 0, 0, 0, 0

def add_regression_line(fig, df, x_col, y_col):
    """手動添加回歸線到Plotly圖表"""
    try:
        # 計算回歸線
        x = df[x_col].dropna().values
        y = df[y_col].dropna().values
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]
        
        slope, intercept, _, _ = calculate_regression(x, y)
        
        # 創建回歸線數據
        x_range = np.linspace(x.min(), x.max(), 100)
        y_pred = slope * x_range + intercept
        
        # 添加回歸線
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=y_pred,
                mode='lines',
                name='回歸線',
                line=dict(color='red', width=2, dash='dash'),
                showlegend=True
            )
        )
        
    except Exception as e:
        pass
    
    return fig

def manual_ols_regression(x, y):
    """手動實現OLS回歸，避免依賴statsmodels，並提供完整統計量"""
    try:
        # 添加常數項
        X = np.column_stack([np.ones(len(x)), x])
        
        # OLS公式: β = (X'X)^{-1}X'y
        XTX = np.dot(X.T, X)
        XTX_inv = np.linalg.inv(XTX)
        beta = np.dot(XTX_inv, np.dot(X.T, y))
        
        # 計算預測值和殘差
        y_pred = np.dot(X, beta)
        residuals = y - y_pred
        
        # 計算統計量
        n = len(x)
        k = 2  # 截距 + 斜率
        
        # 殘差平方和
        ss_res = np.sum(residuals**2)
        
        # 總平方和
        ss_tot = np.sum((y - np.mean(y))**2)
        
        # R²
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # 調整後R²
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - k) if n > k else r_squared
        
        # 標準誤
        sigma2 = ss_res / (n - k)
        var_beta = sigma2 * np.diag(XTX_inv)
        std_err = np.sqrt(var_beta)
        
        # t統計量
        t_values = beta / std_err
        
        # p值（使用t分布）
        p_values = [2 * (1 - stats.t.cdf(np.abs(t), df=n-k)) for t in t_values]
        
        # F統計量
        msr = (ss_tot - ss_res) / (k - 1)
        mse = ss_res / (n - k)
        f_value = msr / mse if mse != 0 else 0
        
        return {
            'intercept': beta[0],
            'slope': beta[1],
            'r_squared': r_squared,
            'adj_r_squared': adj_r_squared,
            'std_err_intercept': std_err[0],
            'std_err_slope': std_err[1],
            't_intercept': t_values[0],
            't_slope': t_values[1],
            'p_intercept': p_values[0],
            'p_slope': p_values[1],
            'f_value': f_value,
            'n': n,
            'residuals': residuals
        }
    except Exception as e:
        st.warning(f"手動回歸計算錯誤: {e}")
        return None

def calculate_gini(series):
    """計算基尼係數 (0=完全平等, 1=完全不平等)"""
    # 確保數值為正
    incomes = np.sort(series.dropna().values)
    incomes = incomes[incomes > 0]
    if len(incomes) == 0: return 0
    
    n = len(incomes)
    index = np.arange(1, n + 1)
    return ((2 * index - n - 1) * incomes).sum() / (n * incomes.sum())

def plot_lorenz_curve(df, team_name="All Teams"):
    """繪製羅倫茲曲線"""
    incomes = np.sort(df['Salary_millions'].dropna().values)
    incomes = incomes[incomes > 0]
    if len(incomes) == 0: return go.Figure(), 0

    # 計算累積比例
    lorenz_curve = np.cumsum(incomes) / incomes.sum()
    lorenz_curve = np.insert(lorenz_curve, 0, 0)
    
    # 理想平等線
    x_axis = np.linspace(0, 1, len(lorenz_curve))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_axis, y=lorenz_curve,
        mode='lines', name='實際分配',
        fill='tozeroy', fillcolor='rgba(26, 35, 126, 0.2)',
        line=dict(color='#1a237e', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines', name='完全平等線',
        line=dict(dash='dash', color='#ef5350')
    ))
    
    gini = calculate_gini(df['Salary_millions'])
    
    fig.update_layout(
        title=f'{team_name} 薪資不平等分析 (Gini: {gini:.3f})',
        xaxis_title='球員累積百分比',
        yaxis_title='薪資累積百分比',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig, gini

def analyze_positional_arbitrage(df):
    """位置套利分析"""
    if 'Position' not in df.columns or 'WAR' not in df.columns:
        return None
        
    # 計算各位置平均數據
    pos_stats = df.groupby('Position').agg({
        'Salary_millions': 'mean',
        'WAR': 'mean',
        'Name': 'count'
    }).reset_index()
    
    # 過濾樣本過少的位置
    pos_stats = pos_stats[pos_stats['Name'] >= 5]
    
    # 計算每1 WAR的成本 (Cost per WAR)
    pos_stats['Cost_per_WAR'] = pos_stats['Salary_millions'] / pos_stats['WAR']
    pos_stats = pos_stats.sort_values('Cost_per_WAR')
    
    return pos_stats

def plot_player_radar(df, player_names):
    """繪製球員雷達比較圖 (使用百分位數)"""
    if not player_names: return None
    
    # 選擇要比較的指標
    metrics = ['Salary_millions', 'WAR', 'value_ratio', 'HR', 'RBI']
    labels = ['薪資', 'WAR', '性價比', '全壘打', '打點']
    
    # 新增原創指標到雷達圖
    if 'WVPI' in df.columns:
        metrics.append('WVPI')
        labels.append('WVPI')
    if 'RAV' in df.columns:
        metrics.append('RAV')
        labels.append('RAV')
    
    fig = go.Figure()
    
    for name in player_names:
        player_data = df[df['Name'] == name].iloc[0]
        
        # 為了讓雷達圖好看，我們計算該球員在全聯盟的百分位數
        values = []
        for metric in metrics:
            if metric in df.columns:
                try:
                    # 計算百分位數 (0-100)
                    percentile = stats.percentileofscore(df[metric].dropna(), player_data[metric])
                    values.append(percentile)
                except:
                    values.append(0)
            else:
                values.append(0)
        
        # 封閉雷達圖
        values.append(values[0])
        plot_labels = labels + [labels[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=plot_labels,
            fill='toself',
            name=f"{name} (PR值)"
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%')
        ),
        title="球員能力PR值對比 (數值為聯盟百分位數)",
        height=450
    )
    return fig

def plot_tpm_matrix(df):
    """繪製雙因子績效矩陣 (TPM)"""
    if 'war_percentile' not in df.columns or 'value_ratio' not in df.columns:
        return None, None
    
    # 計算性價比百分位
    df_temp = df.copy()
    df_temp['value_percentile'] = df_temp['value_ratio'].rank(pct=True) * 100
    
    # 定義象限 - 使用布林遮罩來避免 dtype 問題
    mask_star = (df_temp['war_percentile'] >= 50) & (df_temp['value_percentile'] >= 50)
    mask_premium = (df_temp['war_percentile'] >= 50) & (df_temp['value_percentile'] < 50)
    mask_rookie = (df_temp['war_percentile'] < 50) & (df_temp['value_percentile'] >= 50)
    mask_deadweight = (df_temp['war_percentile'] < 50) & (df_temp['value_percentile'] < 50)
    
    # 使用 loc 和布林遮罩來賦值
    df_temp['TPM_category'] = '未分類'
    df_temp.loc[mask_star, 'TPM_category'] = '明星價值'
    df_temp.loc[mask_premium, 'TPM_category'] = '溢價球星'
    df_temp.loc[mask_rookie, 'TPM_category'] = '潛力新秀'
    df_temp.loc[mask_deadweight, 'TPM_category'] = '球隊冗員'
    
    # 創建散點圖
    fig = px.scatter(
        df_temp,
        x='war_percentile',
        y='value_percentile',
        color='TPM_category',
        hover_name='Name' if 'Name' in df_temp.columns else None,
        hover_data=['Team', 'Position', 'WAR', 'Salary_millions'],
        title='雙因子績效矩陣 (TPM)',
        labels={'war_percentile': 'WAR百分位 (%)', 'value_percentile': '性價比百分位 (%)'},
        color_discrete_map={
            '明星價值': '#2E7D32',  # 綠色
            '溢價球星': '#C62828',  # 紅色
            '潛力新秀': '#FF8F00',  # 橙色
            '球隊冗員': '#757575',   # 灰色
            '未分類': '#000000'      # 黑色
        }
    )
    
    # 添加象限分隔線
    fig.add_hline(y=50, line_dash="dash", line_color="black", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="black", opacity=0.5)
    
    fig.update_layout(
        xaxis_range=[0, 100],
        yaxis_range=[0, 100],
        height=600
    )
    
    return fig, df_temp

# ============================================================
# 側邊欄控制面板
# ============================================================
with st.sidebar:
    st.markdown("## 控制面板")
    
    # 分析選項
    st.markdown("### 選擇分析功能")
    analysis_mode = st.selectbox(
        "選擇要進行的分析",
        ["綜合儀表板", "球員搜尋", "球隊分析", "市場異常偵測", "進階策略分析", "原創財務指標", "公式與變數說明"],
        key="analysis_mode"
    )
    
    st.markdown("---")
    
    # 數據資訊
    st.markdown("### 專題資訊")
    st.markdown("**主題**: MLB薪資市場效率性分析")
    st.markdown("**方法**: 計量經濟學 + 財務分析")
    st.markdown("**目標**: 識別市場異常與投資機會")
    
    st.markdown("---")
    st.markdown(f"**更新時間:** {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# 主內容區域
# ============================================================

# 載入數據
df = load_data()

if df is None:
    st.warning("正在載入數據...")
    st.stop()

# 根據選擇的模組顯示不同內容
if analysis_mode == "綜合儀表板":
    st.markdown('<h2 class="section-title">綜合分析儀表板</h2>', unsafe_allow_html=True)
    
    # 使用說明
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 專題介紹
        **主題**: MLB薪資市場效率性分析  
        **方法**: 計量經濟學 + 財務分析  
        **目標**: 識別市場異常與投資機會
        
        ### 如何使用本儀表板
        1. **查看關鍵指標**：下方的卡片顯示整體數據概況
        2. **探索圖表**：互動式圖表可放大、縮小、懸停查看詳細信息
        3. **篩選數據**：使用圖表上方的篩選器查看特定範圍的數據
        4. **導出數據**：表格部分支持篩選和導出功能
        """)
    
    # 全局篩選條件
    st.markdown("### 數據篩選")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Team' in df.columns:
            all_teams = ["所有球隊"] + sorted(df['Team'].dropna().unique().tolist())
            selected_team = st.selectbox("選擇球隊", all_teams)
    
    with col2:
        if 'WAR' in df.columns:
            war_min, war_max = float(df['WAR'].min()), float(df['WAR'].max())
            war_range = st.slider("WAR範圍", war_min, war_max, (war_min, war_max))
    
    with col3:
        if 'Salary_millions' in df.columns:
            salary_min, salary_max = float(df['Salary_millions'].min()), float(df['Salary_millions'].max())
            salary_range = st.slider("薪資範圍 (百萬美元)", salary_min, salary_max, (salary_min, salary_max))
    
    # 應用篩選
    filtered_df = df.copy()
    
    if 'Team' in df.columns and selected_team != "所有球隊":
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    
    if 'WAR' in df.columns:
        filtered_df = filtered_df[(filtered_df['WAR'] >= war_range[0]) & (filtered_df['WAR'] <= war_range[1])]
    
    if 'Salary_millions' in df.columns:
        filtered_df = filtered_df[(filtered_df['Salary_millions'] >= salary_range[0]) & 
                                 (filtered_df['Salary_millions'] <= salary_range[1])]
    
    # 關鍵指標卡片
    st.markdown("### 關鍵績效指標")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("球員總數", f"{len(filtered_df):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if 'Salary_millions' in filtered_df.columns:
            avg_salary = filtered_df['Salary_millions'].mean()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("平均薪資", f"${avg_salary:.2f}M")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if 'WAR' in filtered_df.columns:
            avg_war = filtered_df['WAR'].mean()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("平均WAR", f"{avg_war:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        if 'WAR' in filtered_df.columns and 'Salary_millions' in filtered_df.columns:
            correlation = filtered_df['WAR'].corr(filtered_df['Salary_millions'])
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("相關係數", f"{correlation:.3f}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 圖表區域
    st.markdown("### 互動式圖表分析")
    
    tab1, tab2, tab3, tab4 = st.tabs(["薪資表現關係", "數據分布", "性價比分析", "市場效率指標"])
    
    with tab1:
        if 'WAR' in filtered_df.columns and 'Salary_millions' in filtered_df.columns:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 散點圖
                fig = px.scatter(
                    filtered_df,
                    x='WAR',
                    y='Salary_millions',
                    hover_name='Name' if 'Name' in filtered_df.columns else None,
                    hover_data=['Team', 'Position'] if all(col in filtered_df.columns for col in ['Team', 'Position']) else None,
                    title='薪資與表現關係圖',
                    labels={'WAR': '勝場貢獻值 (WAR)', 'Salary_millions': '薪資 (百萬美元)'}
                )
                
                # 添加回歸線
                fig = add_regression_line(fig, filtered_df, 'WAR', 'Salary_millions')
                
                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
                # 替換為: st.plotly_chart(fig, width='stretch')
            
            with col2:
                # 統計分析
                x = filtered_df['WAR'].dropna().values
                y = filtered_df['Salary_millions'].dropna().values
                min_len = min(len(x), len(y))
                x = x[:min_len]
                y = y[:min_len]
                
                slope, intercept, correlation, r_squared = calculate_regression(x, y)
                
                st.markdown("#### 回歸分析結果")
                st.write(f"**回歸方程:**")
                st.code(f"薪資 = {slope:.3f} × WAR + {intercept:.3f}")
                st.write(f"**決定係數 R²:** {r_squared:.3f}")
                st.write(f"**解釋力:** {r_squared*100:.1f}%")
                st.write(f"**每1 WAR價值:** ${slope:.2f}M")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Salary_millions' in filtered_df.columns:
                fig1 = px.histogram(
                    filtered_df,
                    x='Salary_millions',
                    nbins=30,
                    title='薪資分布',
                    labels={'Salary_millions': '薪資 (百萬美元)'},
                    marginal="box"
                )
                st.plotly_chart(fig1, use_container_width=True)  # 保留原始參數
        
        with col2:
            if 'WAR' in filtered_df.columns:
                fig2 = px.histogram(
                    filtered_df,
                    x='WAR',
                    nbins=30,
                    title='WAR分布',
                    labels={'WAR': '勝場貢獻值'},
                    marginal="violin"
                )
                st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
    
    with tab3:
        if 'value_ratio' in filtered_df.columns and 'Name' in filtered_df.columns:
            # 性價比排名
            st.markdown("#### 性價比最高球員")
            
            # 篩選出有正面WAR的球員
            positive_war = filtered_df[filtered_df['WAR'] > 0].copy()
            positive_war = positive_war[positive_war['value_ratio'].notna()]
            
            if len(positive_war) > 0:
                top_players = positive_war.nlargest(20, 'value_ratio')
                
                fig = px.bar(
                    top_players,
                    x='Name',
                    y='value_ratio',
                    color='value_ratio',
                    title='性價比最高球員 (前20名)',
                    labels={'value_ratio': '性價比 (WAR/百萬美元)', 'Name': '球員姓名'},
                    hover_data=['Team', 'WAR', 'Salary_millions']
                )
                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
            else:
                st.warning("沒有找到有正面WAR值的球員")
    
    with tab4:
        st.markdown("#### 市場效率指標分析")
        
        if all(col in filtered_df.columns for col in ['WVPI', 'RAV', 'MERI']):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_wvpi = filtered_df['WVPI'].mean()
                st.metric("平均 WVPI", f"{avg_wvpi:.2f}")
                st.caption("加權綜合價值指數")
            
            with col2:
                avg_rav = filtered_df['RAV'].mean()
                st.metric("平均 RAV", f"{avg_rav:.2f}")
                st.caption("風險調整後價值")
            
            with col3:
                avg_meri = filtered_df['MERI'].mean()
                st.metric("平均 MERI", f"{avg_meri:.4f}")
                st.caption("市場效率殘差指數")
            
            # 顯示原創指標的分布
            fig_wvpi = px.histogram(
                filtered_df,
                x='WVPI',
                nbins=30,
                title='WVPI 分布',
                color='WVPI_category' if 'WVPI_category' in filtered_df.columns else None
            )
            st.plotly_chart(fig_wvpi, use_container_width=True)  # 保留原始參數
    
    # 數據表格
    st.markdown("### 詳細數據表格")
    
    # 欄位選擇
    available_cols = filtered_df.columns.tolist()
    
    # 優先顯示的欄位 (加入原創指標)
    priority_cols = ['Name', 'Team', 'Position', 'WAR', 'Salary_millions', 'value_ratio', 'WVPI', 'RAV', 'MERI']
    priority_cols = [col for col in priority_cols if col in available_cols]
    
    # 搜尋功能
    search_col1, search_col2 = st.columns([2, 1])
    
    with search_col1:
        search_term = st.text_input("搜尋球員姓名", "", placeholder="輸入球員姓名關鍵字")
    
    with search_col2:
        sort_by = st.selectbox("排序依據", priority_cols)
    
    # 應用搜尋和排序
    display_df = filtered_df.copy()
    
    if search_term and 'Name' in filtered_df.columns:
        display_df = display_df[display_df['Name'].str.contains(search_term, case=False, na=False)]
    
    display_df = display_df.sort_values(sort_by, ascending=False)
    
    # 顯示數據
    st.dataframe(
        display_df[priority_cols].head(100),
        use_container_width=True,  # 保留原始參數
        height=400
    )
    
    # 下載按鈕
    csv = display_df[priority_cols].to_csv(index=False)
    st.download_button(
        label="下載篩選後數據",
        data=csv,
        file_name=f"mlb_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

elif analysis_mode == "球員搜尋":
    st.markdown('<h2 class="section-title">球員搜尋與比較</h2>', unsafe_allow_html=True)
    
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 功能介紹
        1. **球員搜尋**：輸入球員姓名（支援部分關鍵字）
        2. **球員比較**：選擇多位球員進行詳細比較
        3. **詳細資訊**：點擊球員姓名展開查看完整數據
        
        ### 使用技巧
        - 搜尋時可以使用姓氏或名字的任何部分
        - 最多可同時比較5位球員
        - 所有數據皆可排序和篩選
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 球員搜尋")
        
        # 快速搜尋
        search_term = st.text_input("輸入球員姓名", "", 
                                   placeholder="例如：Ohtani, Trout, Judge...",
                                   key="player_search")
        
        if search_term and 'Name' in df.columns:
            search_results = df[df['Name'].str.contains(search_term, case=False, na=False)]
            
            if len(search_results) > 0:
                st.success(f"找到 {len(search_results)} 位球員")
                
                # 顯示搜尋結果
                for idx, player in search_results.iterrows():
                    with st.expander(f"👤 {player['Name']}", expanded=False):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if 'Team' in df.columns:
                                st.write(f"**球隊:** {player.get('Team', 'N/A')}")
                            if 'Position' in df.columns:
                                st.write(f"**位置:** {player.get('Position', 'N/A')}")
                            if 'WAR' in df.columns:
                                st.write(f"**WAR:** {player.get('WAR', 'N/A'):.2f}")
                            if 'WVPI' in df.columns:
                                st.write(f"**WVPI:** {player.get('WVPI', 'N/A'):.2f}")
                        
                        with col_b:
                            if 'Salary_millions' in df.columns:
                                st.write(f"**薪資:** ${player.get('Salary_millions', 'N/A'):.2f}M")
                            if 'HR' in df.columns:
                                st.write(f"**全壘打:** {player.get('HR', 'N/A')}")
                            if 'RBI' in df.columns:
                                st.write(f"**打點:** {player.get('RBI', 'N/A')}")
                            if 'RAV' in df.columns:
                                st.write(f"**RAV:** {player.get('RAV', 'N/A'):.2f}")
                        
                        if 'value_ratio' in df.columns and pd.notna(player.get('value_ratio')):
                            st.write(f"**性價比:** {player.get('value_ratio', 'N/A'):.3f} WAR/百萬美元")
            else:
                st.warning("找不到符合條件的球員")
                st.info("試試看：使用姓氏或名字的任何部分進行搜尋")
    
    with col2:
        st.markdown("#### 球員比較")
        
        # 球員選擇
        if 'Name' in df.columns:
            # 顯示球員選擇器
            player_options = df['Name'].sort_values().tolist()
            
            selected_players = st.multiselect(
                "選擇要比較的球員",
                player_options,
                max_selections=5,
                help="可選擇最多5位球員進行詳細比較"
            )
            
            if len(selected_players) >= 1:
                compare_df = df[df['Name'].isin(selected_players)]
                
                # 選擇要顯示的欄位 (加入原創指標)
                compare_cols = ['Name', 'Team', 'Position', 'WAR', 'Salary_millions', 'value_ratio', 'WVPI', 'RAV', 'MERI']
                
                # 檢查欄位是否存在
                available_cols = [col for col in compare_cols if col in compare_df.columns]
                
                if len(available_cols) >= 4:  # 至少要有姓名和主要數據
                    st.dataframe(
                        compare_df[available_cols].sort_values('WAR', ascending=False),
                        use_container_width=True,  # 保留原始參數
                        hide_index=True
                    )
                    
                    # 簡單比較圖表
                    if len(selected_players) >= 2:
                        st.markdown("#### 比較圖表")
                        
                        # 新增：雷達圖比較
                        st.markdown("**能力值比較 (PR值雷達圖)**")
                        fig_radar = plot_player_radar(df, selected_players)
                        if fig_radar:
                            st.plotly_chart(fig_radar, use_container_width=True)  # 保留原始參數

                        # 原有的柱狀圖
                        st.markdown("**數值直接比較**")
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=compare_df['Name'],
                            y=compare_df['WAR'],
                            name='WAR',
                            marker_color='blue'
                        ))
                        
                        fig.add_trace(go.Bar(
                            x=compare_df['Name'],
                            y=compare_df['Salary_millions'],
                            name='薪資 (M)',
                            marker_color='green',
                            yaxis='y2'
                        ))
                        
                        fig.update_layout(
                            title='球員WAR與薪資比較',
                            yaxis=dict(title='WAR'),
                            yaxis2=dict(title='薪資 (百萬美元)', overlaying='y', side='right'),
                            barmode='group'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)  # 保留原始參數

elif analysis_mode == "球隊分析":
    st.markdown('<h2 class="section-title">球隊分析</h2>', unsafe_allow_html=True)
    
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 功能介紹
        1. **球隊選擇**：選擇要分析的球隊（可多選）
        2. **效率排名**：比較不同球隊的薪資使用效率
        3. **詳細統計**：查看每支球隊的詳細數據
        4. **投資組合夏普指數 (PSI)**：衡量球隊風險調整後的績效表現
        
        ### 關鍵指標
        - **總WAR**：球隊所有球員的WAR總和
        - **總薪資**：球隊薪資支出總額
        - **效率**：每百萬美元薪資能獲得的WAR
        - **PSI**：投資組合夏普指數，衡量風險調整後的超額績效
        """)
    
    if 'Team' in df.columns:
        # 球隊選擇
        all_teams = sorted(df['Team'].dropna().unique().tolist())
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_teams = st.multiselect(
                "選擇球隊（可多選）",
                all_teams,
                default=all_teams[1:5] if len(all_teams) > 4 else all_teams,
                help="選擇要分析的球隊，預設顯示前4支球隊"
            )
        
        with col2:
            # 分析類型選擇
            analysis_type = st.selectbox(
                "分析類型",
                ["效率排名", "詳細統計", "薪資分布", "薪資不平等分析", "投資組合夏普指數 (PSI)"],
                help="選擇要進行的分析類型"
            )
        
        if selected_teams:
            team_df = df[df['Team'].isin(selected_teams)]
            
            if analysis_type == "效率排名":
                # 計算球隊統計
                team_stats = team_df.groupby('Team').agg({
                    'Name': 'count',
                    'WAR': 'sum',
                    'Salary_millions': 'sum',
                }).round(2).reset_index()
                
                team_stats['efficiency'] = (team_stats['WAR'] / team_stats['Salary_millions']).round(3)
                team_stats = team_stats.rename(columns={
                    'Name': '球員數',
                    'WAR': '總WAR',
                    'Salary_millions': '總薪資(M)'
                })
                
                # 排序選項
                sort_by = st.selectbox("排序方式", ["總WAR", "效率", "總薪資(M)", "球員數"])
                
                if sort_by == "效率":
                    team_stats = team_stats.sort_values('efficiency', ascending=False)
                elif sort_by == "總薪資(M)":
                    team_stats = team_stats.sort_values('總薪資(M)', ascending=False)
                elif sort_by == "球員數":
                    team_stats = team_stats.sort_values('球員數', ascending=False)
                else:  # 總WAR
                    team_stats = team_stats.sort_values('總WAR', ascending=False)
                
                # 顯示排名
                st.dataframe(team_stats, use_container_width=True, hide_index=True)  # 保留原始參數
                
                # 可視化
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.bar(
                        team_stats,
                        x='Team',
                        y='總WAR',
                        title='球隊總WAR排名',
                        color='總WAR',
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig1, use_container_width=True)  # 保留原始參數
                
                with col2:
                    fig2 = px.bar(
                        team_stats,
                        x='Team',
                        y='efficiency',
                        title='球隊效率排名',
                        color='efficiency',
                        color_continuous_scale='plasma'
                    )
                    st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
            
            elif analysis_type == "詳細統計":
                st.markdown("#### 球隊詳細統計")
                
                if 'Team' in team_df.columns:
                    # 為每支球隊創建詳細統計
                    for team in selected_teams:
                        team_players = team_df[team_df['Team'] == team]
                        
                        if len(team_players) > 0:
                            with st.expander(f"{team} - {len(team_players)}位球員", expanded=False):
                                # 球隊摘要指標
                                col_a, col_b, col_c, col_d = st.columns(4)
                                
                                with col_a:
                                    total_war = team_players['WAR'].sum() if 'WAR' in team_players.columns else 0
                                    st.metric("總WAR", f"{total_war:.2f}")
                                
                                with col_b:
                                    total_salary = team_players['Salary_millions'].sum() if 'Salary_millions' in team_players.columns else 0
                                    st.metric("總薪資", f"${total_salary:.2f}M")
                                
                                with col_c:
                                    avg_salary = team_players['Salary_millions'].mean() if 'Salary_millions' in team_players.columns else 0
                                    st.metric("平均薪資", f"${avg_salary:.2f}M")
                                
                                with col_d:
                                    if total_salary > 0 and 'WAR' in team_players.columns:
                                        efficiency = total_war / total_salary
                                        st.metric("效率", f"{efficiency:.3f}")
                                    else:
                                        st.metric("效率", "N/A")
                                
                                # 分頁顯示
                                stat_tab1, stat_tab2, stat_tab3 = st.tabs(["球員列表", "表現分析", "薪資結構"])
                                
                                with stat_tab1:
                                    # 顯示球員列表
                                    display_cols = []
                                    if 'Name' in team_players.columns:
                                        display_cols.append('Name')
                                    if 'Position' in team_players.columns:
                                        display_cols.append('Position')
                                    if 'WAR' in team_players.columns:
                                        display_cols.append('WAR')
                                    if 'Salary_millions' in team_players.columns:
                                        display_cols.append('Salary_millions')
                                    if 'value_ratio' in team_players.columns:
                                        display_cols.append('value_ratio')
                                    if 'WVPI' in team_players.columns:
                                        display_cols.append('WVPI')
                                    
                                    if display_cols:
                                        # 排序選項
                                        sort_option = st.selectbox(
                                            f"排序方式 ({team})",
                                            [col for col in ['WAR', 'Salary_millions', 'value_ratio', 'WVPI'] if col in display_cols],
                                            key=f"sort_{team}"
                                        )
                                        
                                        if sort_option in team_players.columns:
                                            sorted_players = team_players.sort_values(sort_option, ascending=False)
                                            st.dataframe(
                                                sorted_players[display_cols],
                                                use_container_width=True,  # 保留原始參數
                                                hide_index=True
                                            )
                                        else:
                                            st.dataframe(
                                                team_players[display_cols],
                                                use_container_width=True,  # 保留原始參數
                                                hide_index=True
                                            )
                                
                                with stat_tab2:
                                    # 表現分析
                                    if 'WAR' in team_players.columns:
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # WAR分布
                                            fig1 = px.histogram(
                                                team_players,
                                                x='WAR',
                                                nbins=20,
                                                title=f'{team} - WAR分布',
                                                labels={'WAR': '勝場貢獻值'}
                                            )
                                            st.plotly_chart(fig1, use_container_width=True)  # 保留原始參數
                                        
                                        with col2:
                                            # WAR百分位
                                            if 'war_percentile' in team_players.columns:
                                                fig2 = px.box(
                                                    team_players,
                                                    y='war_percentile',
                                                    title=f'{team} - WAR百分位分布',
                                                    labels={'war_percentile': 'WAR百分位 (%)'}
                                                )
                                                st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
                                
                                with stat_tab3:
                                    # 薪資結構分析
                                    if 'Salary_millions' in team_players.columns:
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # 薪資分布
                                            fig3 = px.pie(
                                                team_players,
                                                values='Salary_millions',
                                                names='Position' if 'Position' in team_players.columns else None,
                                                title=f'{team} - 薪資按位置分布',
                                                hole=0.3
                                            )
                                            st.plotly_chart(fig3, use_container_width=True)  # 保留原始參數
                                        
                                        with col2:
                                            # 薪資級別分析
                                            if 'salary_category' in team_players.columns:
                                                salary_cat_counts = team_players['salary_category'].value_counts()
                                                fig4 = px.bar(
                                                    x=salary_cat_counts.index,
                                                    y=salary_cat_counts.values,
                                                    title=f'{team} - 薪資級別分布',
                                                    labels={'x': '薪資級別', 'y': '球員數'}
                                                )
                                                st.plotly_chart(fig4, use_container_width=True)  # 保留原始參數
                        
                        else:
                            st.info(f"球隊 {team} 沒有可用的球員數據")

            elif analysis_type == "薪資分布":
                st.markdown("#### 球隊薪資分布分析")
                
                if 'Salary_millions' in team_df.columns and 'Team' in team_df.columns:
                    # 使用標籤頁組織不同視圖
                    dist_tab1, dist_tab2, dist_tab3 = st.tabs(["視覺化分布", "統計摘要", "球隊比較"])
                    
                    with dist_tab1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 箱形圖顯示分布
                            fig_box = px.box(
                                team_df,
                                x='Team',
                                y='Salary_millions',
                                title='各球隊薪資分布',
                                labels={'Salary_millions': '薪資（百萬美元）'},
                                color='Team'
                            )
                            fig_box.update_layout(showlegend=False)
                            st.plotly_chart(fig_box, use_container_width=True)  # 保留原始參數
                        
                        with col2:
                            # 小提琴圖顯示概率密度
                            fig_violin = px.violin(
                                team_df,
                                x='Team',
                                y='Salary_millions',
                                box=True,
                                points="outliers",
                                title='薪資密度分布',
                                labels={'Salary_millions': '薪資（百萬美元）'}
                            )
                            st.plotly_chart(fig_violin, use_container_width=True)  # 保留原始參數
                    
                    with dist_tab2:
                        # 詳細統計表格
                        stats_cols = ['Team', 'Salary_millions']
                        if 'WAR' in team_df.columns:
                            stats_cols.append('WAR')
                        if 'value_ratio' in team_df.columns:
                            stats_cols.append('value_ratio')
                        
                        stats_df = team_df[stats_cols].groupby('Team').agg({
                            'Salary_millions': ['count', 'mean', 'median', 'std', 'min', 'max', 'sum'],
                            **({'WAR': 'sum'} if 'WAR' in stats_cols else {}),
                            **({'value_ratio': 'mean'} if 'value_ratio' in stats_cols else {})
                        }).round(2)
                        
                        # 扁平化多層索引
                        stats_df.columns = ['_'.join(col).strip() for col in stats_df.columns.values]
                        stats_df = stats_df.reset_index()
                        
                        # 重新命名欄位
                        column_rename = {
                            'Salary_millions_count': '球員數',
                            'Salary_millions_mean': '平均薪資',
                            'Salary_millions_median': '薪資中位數',
                            'Salary_millions_std': '薪資標準差',
                            'Salary_millions_min': '最低薪資',
                            'Salary_millions_max': '最高薪資',
                            'Salary_millions_sum': '薪資總額'
                        }
                        
                        if 'WAR_sum' in stats_df.columns:
                            column_rename['WAR_sum'] = '總WAR'
                        if 'value_ratio_mean' in stats_df.columns:
                            column_rename['value_ratio_mean'] = '平均性價比'
                        
                        stats_df = stats_df.rename(columns=column_rename)
                        
                        st.dataframe(stats_df, use_container_width=True, hide_index=True)  # 保留原始參數
                    
                    with dist_tab3:
                        # 球隊間比較
                        st.markdown("##### 球隊間薪資結構比較")
                        
                        comparison_cols = st.multiselect(
                            "選擇比較指標",
                            ['平均薪資', '薪資中位數', '薪資總額', '球員數', '總WAR', '平均性價比'],
                            default=['平均薪資', '總WAR']
                        )
                        
                        if comparison_cols and stats_df is not None:
                            # 確保選擇的欄位存在
                            available_cols = [col for col in comparison_cols if col in stats_df.columns]
                            
                            if available_cols:
                                comparison_df = stats_df[['Team'] + available_cols]
                                
                                # 創建比較圖表
                                fig = go.Figure()
                                
                                for col in available_cols:
                                    fig.add_trace(go.Bar(
                                        name=col,
                                        x=comparison_df['Team'],
                                        y=comparison_df[col],
                                        text=comparison_df[col].round(2),
                                        textposition='auto'
                                    ))
                                
                                fig.update_layout(
                                    title='球隊間指標比較',
                                    barmode='group',
                                    xaxis_title="球隊",
                                    yaxis_title="數值"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
                            else:
                                st.info("請選擇有效的比較指標")
                
                else:
                    st.warning("⚠️ 無法進行薪資分布分析：缺少必要的薪資或球隊數據")
            
            # 新增：薪資不平等分析區塊
            elif analysis_type == "薪資不平等分析":
                st.markdown("#### 球隊薪資結構與不平等 (Gini Coefficient)")
                
                for team in selected_teams:
                    team_data = team_df[team_df['Team'] == team]
                    
                    with st.expander(f"{team} - 薪資不平等分析", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 羅倫茲曲線與 Gini
                            fig_lorenz, gini = plot_lorenz_curve(team_data, team)
                            st.plotly_chart(fig_lorenz, use_container_width=True)  # 保留原始參數
                            
                            # Gini 解讀
                            if gini > 0.5:
                                st.warning(f"⚠️ 薪資分配極度不均 (Gini: {gini:.3f}) - 球隊資源高度集中於少數球星")
                            else:
                                st.success(f"✅ 薪資分配相對平均 (Gini: {gini:.3f}) - 團隊薪資結構較為均衡")

                        with col2:
                            # 薪資級別分布
                            if 'salary_category' in team_data.columns:
                                cat_counts = team_data['salary_category'].value_counts()
                                fig2 = px.pie(
                                    values=cat_counts.values,
                                    names=cat_counts.index,
                                    title=f'{team} 薪資級別分布',
                                    hole=0.4
                                )
                                st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
            
            elif analysis_type == "投資組合夏普指數 (PSI)":
                st.markdown("#### 投資組合夏普指數 (Portfolio Sharpe Index)")
                st.markdown("""
                **PSI** 衡量球隊風險調整後的績效表現，類似夏普比率。
                
                $$ \\text{PSI} = \\frac{\\text{總WAR} - \\text{總薪資} \\times \\bar{e}_{\\text{league}}}{\\sigma_{\\text{WAR}}^{\\text{team}}} $$
                
                其中：
                - $\\bar{e}_{\\text{league}}$：聯盟平均效率（每百萬美元可獲得的WAR）
                - $\\sigma_{\\text{WAR}}^{\\text{team}}$：球隊內部球員WAR的標準差（衡量風險）
                """)
                
                # 計算聯盟平均效率
                league_efficiency = df['WAR'].sum() / df['Salary_millions'].sum()
                
                # 計算每支球隊的PSI
                team_psi_list = []
                for team in selected_teams:
                    team_data = team_df[team_df['Team'] == team]
                    
                    if len(team_data) >= 3:  # 至少需要3個球員
                        total_war = team_data['WAR'].sum()
                        total_salary = team_data['Salary_millions'].sum()
                        expected_war = total_salary * league_efficiency
                        excess_war = total_war - expected_war
                        team_risk = team_data['WAR'].std()
                        
                        psi = excess_war / team_risk if team_risk > 0 else 0
                        
                        team_psi_list.append({
                            'Team': team,
                            '總WAR': total_war,
                            '總薪資(M)': total_salary,
                            '預期WAR': expected_war,
                            '超額WAR': excess_war,
                            '球隊風險': team_risk,
                            'PSI': psi
                        })
                
                if team_psi_list:
                    psi_df = pd.DataFrame(team_psi_list)
                    
                    # 顯示PSI排名
                    psi_df_sorted = psi_df.sort_values('PSI', ascending=False)
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.dataframe(
                            psi_df_sorted[['Team', 'PSI', '超額WAR', '球隊風險']].round(3),
                            use_container_width=True,  # 保留原始參數
                            hide_index=True
                        )
                    
                    with col2:
                        # PSI分類 (依據 new_variables.md 5.6 節)
                        conditions = [
                            psi_df_sorted['PSI'] > 1.5,
                            (psi_df_sorted['PSI'] > 0.5) & (psi_df_sorted['PSI'] <= 1.5),
                            (psi_df_sorted['PSI'] > -0.5) & (psi_df_sorted['PSI'] <= 0.5),
                            (psi_df_sorted['PSI'] > -1.5) & (psi_df_sorted['PSI'] <= -0.5),
                            psi_df_sorted['PSI'] <= -1.5
                        ]
                        categories = ['卓越管理', '良好管理', '平庸管理', '效率不佳', '糟糕管理']
                        psi_df_sorted['管理評價'] = np.select(conditions, categories, default='未知')
                        
                        st.dataframe(
                            psi_df_sorted[['Team', 'PSI', '管理評價']], 
                            use_container_width=True,  # 保留原始參數
                            hide_index=True
                        )
                    
                    # 可視化
                    fig = px.bar(
                        psi_df_sorted,
                        x='Team',
                        y='PSI',
                        color='PSI',
                        color_continuous_scale='RdYlGn',
                        title='球隊投資組合夏普指數 (PSI) 排名',
                        labels={'PSI': '投資組合夏普指數'}
                    )
                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig.add_hline(y=0.5, line_dash="dash", line_color="green", opacity=0.3)
                    fig.add_hline(y=-0.5, line_dash="dash", line_color="red", opacity=0.3)
                    
                    st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
                    
                    # PSI 解讀
                    st.markdown("**PSI 解讀**")
                    st.markdown("""
                    - **PSI > 1.5**：卓越管理（光芒、道奇等級）
                    - **0.5 < PSI ≤ 1.5**：良好管理
                    - **-0.5 < PSI ≤ 0.5**：平庸管理
                    - **-1.5 < PSI ≤ -0.5**：效率不佳
                    - **PSI ≤ -1.5**：糟糕管理（需要重組）
                    """)
                else:
                    st.warning("所選球隊數據不足，無法計算PSI")

elif analysis_mode == "市場異常偵測":
    st.markdown('<h2 class="section-title">市場異常偵測</h2>', unsafe_allow_html=True)
    
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 功能介紹
        1. **異常偵測**：基於回歸分析識別被高估/低估的球員
        2. **閾值調整**：可調整異常值的敏感度
        3. **詳細分析**：查看每位異常球員的詳細分析
        
        ### 分析方法
        - 使用線性回歸建立WAR與薪資的關係模型
        - 計算每位球員的預期薪資
        - 比較實際薪資與預期薪資的差異
        - 識別差異超過閾值的球員為異常值
        """)
    
    if 'WAR' in df.columns and 'Salary_millions' in df.columns:
        # 計算預期薪資
        X = df[['WAR']].dropna().values
        y = df['Salary_millions'].dropna().values
        
        min_len = min(len(X), len(y))
        X = X[:min_len]
        y = y[:min_len]
        
        A = np.vstack([X.flatten(), np.ones(min_len)]).T
        slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
        
        # 創建一個新的 DataFrame 來避免警告
        df_clean = df.copy()
        df_clean = df_clean.dropna(subset=['WAR', 'Salary_millions'])
        df_clean['expected_salary'] = slope * df_clean['WAR'] + intercept
        df_clean['salary_residual'] = df_clean['Salary_millions'] - df_clean['expected_salary']
        df_clean['residual_percent'] = (df_clean['salary_residual'] / df_clean['expected_salary']) * 100
        
        # 合併回原 DataFrame
        df = df.merge(
            df_clean[['expected_salary', 'salary_residual', 'residual_percent']], 
            left_index=True, 
            right_index=True, 
            how='left'
        )
        
        # 閾值設定
        st.markdown("### 偵測設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            threshold = st.slider(
                "異常值閾值 (%)", 
                10, 50, 30,
                help="設定差異百分比閾值，值越高表示越嚴格的偵測標準"
            )
        
        with col2:
            min_war = st.slider(
                "最小WAR要求",
                0.0, float(df['WAR'].max()), 1.0,
                help="只分析WAR高於此值的球員，避免極端小樣本影響"
            )
        
        # 篩選數據
        analysis_df = df[df['WAR'] >= min_war].copy()
        
        # 識別異常值
        undervalued = analysis_df[analysis_df['residual_percent'] < -threshold].sort_values('residual_percent')
        overvalued = analysis_df[analysis_df['residual_percent'] > threshold].sort_values('residual_percent', ascending=False)
        
        # 顯示結果摘要
        st.markdown("### 偵測結果")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("分析球員數", len(analysis_df))
        
        with col2:
            st.metric("被低估球員", len(undervalued))
        
        with col3:
            st.metric("被高估球員", len(overvalued))
        
        # 詳細結果
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 被低估球員 (< -{threshold}%)")
            
            if len(undervalued) > 0:
                # 準備要顯示的欄位
                display_data = []
                for idx, player in undervalued.head(20).iterrows():
                    row = {
                        'Name': player.get('Name', 'N/A'),
                        'Team': player.get('Team', 'N/A'),
                        'WAR': round(player.get('WAR', 0), 2),
                        'Salary_millions': round(player.get('Salary_millions', 0), 2),
                    }
                    if 'expected_salary' in player:
                        row['expected_salary'] = round(player['expected_salary'], 2)
                    if 'residual_percent' in player:
                        row['residual_percent'] = round(player['residual_percent'], 1)
                    display_data.append(row)
                
                undervalued_display = pd.DataFrame(display_data)
                
                # 設定欄位格式
                column_config = {
                    'Name': '姓名',
                    'Team': '球隊',
                    'WAR': 'WAR',
                    'Salary_millions': st.column_config.NumberColumn('實際薪資', format='$%.2fM')
                }
                
                if 'expected_salary' in undervalued_display.columns:
                    column_config['expected_salary'] = st.column_config.NumberColumn('預期薪資', format='$%.2fM')
                if 'residual_percent' in undervalued_display.columns:
                    column_config['residual_percent'] = st.column_config.NumberColumn('差異%', format='%.1f%%')
                
                st.dataframe(
                    undervalued_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_config
                )
                
                # 下載按鈕
                csv1 = undervalued_display.to_csv(index=False)
                st.download_button(
                    label="📥 下載被低估球員名單",
                    data=csv1,
                    file_name=f"undervalued_players_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_undervalued"
                )
            else:
                st.info("未發現被低估的球員")
        
        with col2:
            st.markdown(f"#### 被高估球員 (> {threshold}%)")
            
            if len(overvalued) > 0:
                # 準備要顯示的欄位
                display_data = []
                for idx, player in overvalued.head(20).iterrows():
                    row = {
                        'Name': player.get('Name', 'N/A'),
                        'Team': player.get('Team', 'N/A'),
                        'WAR': round(player.get('WAR', 0), 2),
                        'Salary_millions': round(player.get('Salary_millions', 0), 2),
                    }
                    if 'expected_salary' in player:
                        row['expected_salary'] = round(player['expected_salary'], 2)
                    if 'residual_percent' in player:
                        row['residual_percent'] = round(player['residual_percent'], 1)
                    display_data.append(row)
                
                overvalued_display = pd.DataFrame(display_data)
                
                # 設定欄位格式
                column_config = {
                    'Name': '姓名',
                    'Team': '球隊',
                    'WAR': 'WAR',
                    'Salary_millions': st.column_config.NumberColumn('實際薪資', format='$%.2fM')
                }
                
                if 'expected_salary' in overvalued_display.columns:
                    column_config['expected_salary'] = st.column_config.NumberColumn('預期薪資', format='$%.2fM')
                if 'residual_percent' in overvalued_display.columns:
                    column_config['residual_percent'] = st.column_config.NumberColumn('差異%', format='%.1f%%')
                
                st.dataframe(
                    overvalued_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_config
                )
                
                # 下載按鈕
                csv2 = overvalued_display.to_csv(index=False)
                st.download_button(
                    label="📥 下載被高估球員名單",
                    data=csv2,
                    file_name=f"overvalued_players_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_overvalued"
                )
            else:
                st.info("未發現被高估的球員")

# 新增：進階策略分析頁面
elif analysis_mode == "進階策略分析":
    st.markdown('<h2 class="section-title">進階策略分析 (Moneyball & Arbitrage)</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>分析說明：</b> 本模組運用 Moneyball 概念，分析不同守備位置的「購買成本」，尋找市場上的套利機會。
    同時提供手動 OLS 回歸模型檢驗，以供進階統計驗證。
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["位置套利分析 (Moneyball)", "手動 OLS 回歸驗證"])
    
    with tab1:
        st.markdown("### 位置價值與套利分析")
        st.markdown("分析哪個守備位置的「每勝場成本 (Cost per WAR)」最低，尋找市場定價效率較差的領域。")

        pos_arbitrage = analyze_positional_arbitrage(df)
        
        if pos_arbitrage is not None:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_pos = px.bar(
                    pos_arbitrage,
                    x='Position',
                    y='Cost_per_WAR',
                    color='Cost_per_WAR',
                    title='各守備位置的購買成本 (每1 WAR價格)',
                    labels={'Cost_per_WAR': '每單位WAR成本($M)', 'Position': '守備位置'},
                    color_continuous_scale='RdYlGn_r' # 成本越低越綠
                )
                st.plotly_chart(fig_pos, use_container_width=True)  # 保留原始參數
                
            with col2:
                st.markdown("**分析洞察**")
                cheapest = pos_arbitrage.iloc[0]
                most_expensive = pos_arbitrage.iloc[-1]
                
                st.success(f"💰 **最高CP值位置: {cheapest['Position']}**\n\n平均每1 WAR僅需 ${cheapest['Cost_per_WAR']:.2f}M")
                st.error(f"💸 **最昂貴位置: {most_expensive['Position']}**\n\n平均每1 WAR高達 ${most_expensive['Cost_per_WAR']:.2f}M")
                
                st.markdown("---")
                st.dataframe(
                    pos_arbitrage[['Position', 'Cost_per_WAR', 'WAR', 'Salary_millions']]
                    .style.format({'Cost_per_WAR': '{:.2f}', 'WAR': '{:.1f}', 'Salary_millions': '${:.1f}M'}),
                    use_container_width=True,  # 保留原始參數
                    hide_index=True
                )
    
    with tab2:
        st.markdown("### 手動 OLS 回歸模型驗證")
        st.markdown("手動計算最小平方法 (Ordinary Least Squares)，提供完整統計檢定數據。")
        
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("選擇自變數 (X)", ['WAR', 'HR', 'RBI', 'ERA'], index=0)
        with col2:
            y_col = st.selectbox("選擇依變數 (Y)", ['Salary_millions', 'value_ratio'], index=0)
            
        if x_col in df.columns and y_col in df.columns:
            data_reg = df[[x_col, y_col]].dropna()
            
            if len(data_reg) > 10:
                result = manual_ols_regression(data_reg[x_col].values, data_reg[y_col].values)
                
                if result:
                    st.markdown("#### 回歸統計結果")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("R² (決定係數)", f"{result['r_squared']:.4f}")
                    c2.metric("調整後 R²", f"{result['adj_r_squared']:.4f}")
                    c3.metric("F-Statistic", f"{result['f_value']:.2f}")
                    c4.metric("樣本數 (n)", result['n'])
                    
                    st.markdown("#### 係數表")
                    coef_data = {
                        "變數": ["截距 (Intercept)", f"斜率 ({x_col})"],
                        "係數 (Coef)": [result['intercept'], result['slope']],
                        "標準誤 (Std Err)": [result['std_err_intercept'], result['std_err_slope']],
                        "t值 (t-stat)": [result['t_intercept'], result['t_slope']],
                        "P值 (P>|t|)": [result['p_intercept'], result['p_slope']]
                    }
                    st.dataframe(pd.DataFrame(coef_data).style.format({
                        "係數 (Coef)": "{:.4f}",
                        "標準誤 (Std Err)": "{:.4f}",
                        "t值 (t-stat)": "{:.2f}",
                        "P值 (P>|t|)": "{:.4f}"
                    }), use_container_width=True, hide_index=True)  # 保留原始參數
                    
                    # 顯著性判斷
                    if result['p_slope'] < 0.05:
                        st.success(f"✅ 變數 **{x_col}** 對 **{y_col}** 有顯著影響 (P < 0.05)")
                    else:
                        st.warning(f"⚠️ 變數 **{x_col}** 對 **{y_col}** 的影響不顯著 (P >= 0.05)")
            else:
                st.error("樣本數不足，無法進行回歸分析")

# 新增：原創財務指標頁面
elif analysis_mode == "原創財務指標":
    st.markdown('<h2 class="section-title">原創財務指標分析</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>原創指標說明：</b> 本模組展示根據財務學概念設計的六個原創指標，用於評估MLB球員的市場價值、投資效率與風險調整後績效。
    這些指標借鑑了資本資產定價模型(CAPM)、夏普比率、折現現金流模型、迴歸殘差分析與基尼係數。
    </div>
    """, unsafe_allow_html=True)
    
    # 檢查是否有計算原創指標
    if all(col in df.columns for col in ['WVPI', 'RAV', 'MERI']):
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "WVPI (加權綜合價值指數)", 
            "RAV (風險調整後價值)", 
            "MERI (市場效率殘差指數)",
            "TPM (雙因子績效矩陣)",
            "PSI (投資組合夏普指數)",
            "SEI (同步效率指數)"
        ])
        
        with tab1:
            st.markdown("### 加權綜合價值指數 (WVPI)")
            st.markdown("""
            **WVPI** 是一個多維度的球員評估指標，結合了絕對表現、效率、相對排名與成本效益。
            
            $$ \\text{WVPI} = w_1 \\times \\text{WAR} + w_2 \\times \\frac{\\text{WAR}}{\\text{Salary}} + w_3 \\times P_{\\text{WAR}} + w_4 \\times (100 - P_{\\text{Salary}}) $$
            
            **權重設定**: $w_1=0.35$ (絕對表現), $w_2=0.30$ (效率), $w_3=0.20$ (相對表現), $w_4=0.15$ (相對成本)
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # WVPI 排名
                st.markdown("#### WVPI 最高球員 (前20名)")
                top_wvpi = df.nlargest(20, 'WVPI')[['Name', 'Team', 'Position', 'WAR', 'Salary_millions', 'WVPI', 'WVPI_category']]
                st.dataframe(top_wvpi, use_container_width=True, hide_index=True)  # 保留原始參數
            
            with col2:
                # WVPI 分布
                fig = px.histogram(
                    df,
                    x='WVPI',
                    color='WVPI_category',
                    nbins=40,
                    title='WVPI 分布與分類',
                    labels={'WVPI': '加權綜合價值指數'}
                )
                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
            
            # WVPI 分類解讀
            st.markdown("**WVPI 分類解讀**")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                top_count = len(df[df['WVPI_category'] == '頂級球星'])
                st.metric("頂級球星", top_count)
            with col2:
                good_count = len(df[df['WVPI_category'] == '優質球員'])
                st.metric("優質球員", good_count)
            with col3:
                avg_count = len(df[df['WVPI_category'] == '普通球員'])
                st.metric("普通球員", avg_count)
            with col4:
                low_count = len(df[df['WVPI_category'] == '效率待提升'])
                st.metric("效率待提升", low_count)
            with col5:
                bad_count = len(df[df['WVPI_category'] == '問題合約'])
                st.metric("問題合約", bad_count)
        
        with tab2:
            st.markdown("### 風險調整後價值 (RAV)")
            st.markdown("""
            **RAV** 借鑑夏普比率，將球員的表現波動性納入評估，衡量風險調整後的超額貢獻。
            
            $$ \\text{RAV} = \\frac{\\text{WAR} - \\text{WAR}_{\\text{min}}}{\\sigma_{\\text{WAR}} + 1} \\times \\frac{\\text{Median}(\\text{Salary})}{\\text{Salary}} $$
            
            其中 $\\text{WAR}_{\\text{min}}$ 為替補球員水準，$\\sigma_{\\text{WAR}}$ 為表現標準差。
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # RAV 排名
                st.markdown("#### RAV 最高球員 (前20名)")
                top_rav = df.nlargest(20, 'RAV')[['Name', 'Team', 'Position', 'WAR', 'Salary_millions', 'RAV', 'RAV_category']]
                st.dataframe(top_rav, use_container_width=True, hide_index=True)  # 保留原始參數
            
            with col2:
                # RAV 分布
                fig = px.scatter(
                    df,
                    x='WAR',
                    y='RAV',
                    color='RAV_category',
                    hover_name='Name',
                    title='RAV vs WAR 關係圖',
                    labels={'WAR': '勝場貢獻值', 'RAV': '風險調整後價值'}
                )
                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
        
        with tab3:
            st.markdown("### 市場效率殘差指數 (MERI)")
            st.markdown("""
            **MERI** 基於迴歸分析的殘差概念，加入非線性權重，識別市場異常。
            
            $$ \\text{MERI}_i = \\frac{\\text{Salary}_i - \\widehat{\\text{Salary}}_i}{\\widehat{\\text{Salary}}_i} \\times \\ln(1 + \\text{WAR}_i) $$
            
            MERI > 0：被高估，MERI < 0：被低估。
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 最被低估球員
                st.markdown("#### 最被低估球員 (MERI < 0)")
                undervalued_meri = df[df['MERI'] < 0].nsmallest(20, 'MERI')[['Name', 'Team', 'WAR', 'Salary_millions', 'MERI', 'MERI_category']]
                st.dataframe(undervalued_meri, use_container_width=True, hide_index=True)  # 保留原始參數
            
            with col2:
                # 最被高估球員
                st.markdown("#### 最被高估球員 (MERI > 0)")
                overvalued_meri = df[df['MERI'] > 0].nlargest(20, 'MERI')[['Name', 'Team', 'WAR', 'Salary_millions', 'MERI', 'MERI_category']]
                st.dataframe(overvalued_meri, use_container_width=True, hide_index=True)  # 保留原始參數
            
            # MERI 分布
            fig = px.histogram(
                df,
                x='MERI',
                color='MERI_category',
                nbins=50,
                title='MERI 分布 (市場效率殘差)',
                labels={'MERI': '市場效率殘差指數'}
            )
            st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
        
        with tab4:
            st.markdown("### 雙因子績效矩陣 (TPM)")
            st.markdown("""
            **TPM** 是一個2×2的分類矩陣，根據WAR百分位和性價比百分位將球員分為四類。
            
            | 象限 | WAR百分位 | 性價比百分位 | 類別 |
            |------|-----------|--------------|------|
            | Q1 | ≥ 50 | ≥ 50 | 明星價值 |
            | Q2 | ≥ 50 | < 50 | 溢價球星 |
            | Q3 | < 50 | ≥ 50 | 潛力新秀 |
            | Q4 | < 50 | < 50 | 球隊冗員 |
            """)
            
            # 繪製 TPM 矩陣
            tpm_fig, tpm_df = plot_tpm_matrix(df)
            if tpm_fig is not None:
                st.plotly_chart(tpm_fig, use_container_width=True)  # 保留原始參數
                
                # 顯示各象限統計
                st.markdown("#### 各象限球員分佈")
                quadrant_counts = tpm_df['TPM_category'].value_counts().reset_index()
                quadrant_counts.columns = ['類別', '人數']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    star_count = quadrant_counts[quadrant_counts['類別'] == '明星價值']['人數'].values[0] if '明星價值' in quadrant_counts['類別'].values else 0
                    st.metric("⭐ 明星價值", star_count)
                with col2:
                    premium_count = quadrant_counts[quadrant_counts['類別'] == '溢價球星']['人數'].values[0] if '溢價球星' in quadrant_counts['類別'].values else 0
                    st.metric("💰 溢價球星", premium_count)
                with col3:
                    rookie_count = quadrant_counts[quadrant_counts['類別'] == '潛力新秀']['人數'].values[0] if '潛力新秀' in quadrant_counts['類別'].values else 0
                    st.metric("🌱 潛力新秀", rookie_count)
                with col4:
                    deadweight_count = quadrant_counts[quadrant_counts['類別'] == '球隊冗員']['人數'].values[0] if '球隊冗員' in quadrant_counts['類別'].values else 0
                    st.metric("📉 球隊冗員", deadweight_count)
        
        with tab5:
            st.markdown("### 投資組合夏普指數 (PSI)")
            st.markdown("""
            **PSI** 將球隊視為投資組合，評估風險調整後的績效表現。
            
            $$ \\text{PSI}_t = \\frac{\\text{WAR}_t^{\\text{team}} - \\text{Salary}_t^{\\text{team}} \\times \\bar{e}_{\\text{league}}}{\\sigma_{\\text{WAR}}^{\\text{team}}} $$
            
            其中 $\\bar{e}_{\\text{league}}$ 為聯盟平均效率，$\\sigma_{\\text{WAR}}^{\\text{team}}$ 為球隊內部風險。
            """)
            
            # 計算聯盟平均效率
            league_efficiency = df['WAR'].sum() / df['Salary_millions'].sum()
            
            # 計算各球隊 PSI
            team_psi_data = []
            for team in df['Team'].unique():
                team_data = df[df['Team'] == team]
                if len(team_data) >= 3:
                    psi = calculate_team_psi(team_data, league_efficiency)
                    team_psi_data.append({
                        'Team': team,
                        'PSI': psi,
                        '總WAR': team_data['WAR'].sum(),
                        '總薪資': team_data['Salary_millions'].sum(),
                        '球員數': len(team_data)
                    })
            
            if team_psi_data:
                team_psi_df = pd.DataFrame(team_psi_data).sort_values('PSI', ascending=False)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.dataframe(
                        team_psi_df[['Team', 'PSI', '總WAR', '總薪資']].round(3),
                        use_container_width=True,  # 保留原始參數
                        hide_index=True
                    )
                
                with col2:
                    # PSI 分類
                    conditions = [
                        team_psi_df['PSI'] > 1.5,
                        (team_psi_df['PSI'] > 0.5) & (team_psi_df['PSI'] <= 1.5),
                        (team_psi_df['PSI'] > -0.5) & (team_psi_df['PSI'] <= 0.5),
                        (team_psi_df['PSI'] > -1.5) & (team_psi_df['PSI'] <= -0.5),
                        team_psi_df['PSI'] <= -1.5
                    ]
                    categories = ['卓越管理', '良好管理', '平庸管理', '效率不佳', '糟糕管理']
                    team_psi_df['管理評價'] = np.select(conditions, categories, default='未知')
                    
                    eval_counts = team_psi_df['管理評價'].value_counts()
                    fig = px.pie(
                        values=eval_counts.values,
                        names=eval_counts.index,
                        title='球隊管理評價分布',
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
                
                # PSI 排名圖
                fig = px.bar(
                    team_psi_df,
                    x='Team',
                    y='PSI',
                    color='PSI',
                    color_continuous_scale='RdYlGn',
                    title='各球隊 PSI 排名',
                    labels={'PSI': '投資組合夏普指數'}
                )
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
        
        with tab6:
            st.markdown("### 同步效率指數 (SEI)")
            st.markdown("""
            **SEI** 結合市場相關性與分配公平性，是一個總體市場健康指標。
            
            $$ \\text{SEI} = \\rho(\\text{WAR}, \\text{Salary}) \\times (1 - G_{\\text{Salary}}) $$
            
            其中 $\\rho$ 為WAR與薪資的相關係數，$G$ 為薪資的基尼係數。
            """)
            
            # 計算 SEI
            correlation, gini, sei = calculate_sei(df)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("WAR-薪資相關係數 (ρ)", f"{correlation:.4f}")
                if correlation > 0.7:
                    st.success("高度相關 (市場有效率)")
                elif correlation > 0.3:
                    st.info("中度相關")
                else:
                    st.warning("低度相關 (市場無效率)")
            
            with col2:
                st.metric("薪資基尼係數 (G)", f"{gini:.4f}")
                if gini < 0.3:
                    st.success("分配平均")
                elif gini < 0.5:
                    st.info("中度不均")
                else:
                    st.warning("極度不均 (贏者全拿)")
            
            with col3:
                st.metric("同步效率指數 (SEI)", f"{sei:.4f}")
                if sei > 0.7:
                    st.success("健康市場")
                elif sei > 0.4:
                    st.info("正常市場")
                elif sei > 0.2:
                    st.warning("市場失調")
                else:
                    st.error("市場失靈")
            
            # 繪製市場狀態圖
            st.markdown("#### 市場狀態分析")
            
            # 創建四種市場狀態的象限圖
            fig = go.Figure()
            
            # 添加四個象限的背景
            fig.add_shape(type="rect", x0=0, y0=0, x1=0.5, y1=0.5,
                         line=dict(color="rgba(255,0,0,0.3)"), fillcolor="rgba(255,0,0,0.1)")
            fig.add_shape(type="rect", x0=0.5, y0=0, x1=1, y1=0.5,
                         line=dict(color="rgba(255,165,0,0.3)"), fillcolor="rgba(255,165,0,0.1)")
            fig.add_shape(type="rect", x0=0, y0=0.5, x1=0.5, y1=1,
                         line=dict(color="rgba(0,255,0,0.3)"), fillcolor="rgba(0,255,0,0.1)")
            fig.add_shape(type="rect", x0=0.5, y0=0.5, x1=1, y1=1,
                         line=dict(color="rgba(0,0,255,0.3)"), fillcolor="rgba(0,0,255,0.1)")
            
            # 添加市場狀態標籤
            fig.add_annotation(x=0.25, y=0.25, text="混亂市場", showarrow=False, font=dict(size=12, color="gray"))
            fig.add_annotation(x=0.75, y=0.25, text="平均主義", showarrow=False, font=dict(size=12, color="gray"))
            fig.add_annotation(x=0.25, y=0.75, text="菁英市場", showarrow=False, font=dict(size=12, color="gray"))
            fig.add_annotation(x=0.75, y=0.75, text="理想市場", showarrow=False, font=dict(size=12, color="gray"))
            
            # 添加當前市場位置
            fig.add_trace(go.Scatter(
                x=[gini],
                y=[correlation],
                mode='markers+text',
                marker=dict(size=20, color='red', symbol='star'),
                text=['當前市場'],
                textposition='top center',
                name='當前位置'
            ))
            
            fig.update_layout(
                title='市場狀態矩陣',
                xaxis_title='薪資基尼係數 (G) → 不公平程度',
                yaxis_title='WAR-薪資相關係數 (ρ) → 效率程度',
                xaxis_range=[0, 1],
                yaxis_range=[0, 1],
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
            
            # 市場狀態解讀
            st.markdown("""
            **市場狀態解讀**
            - **理想市場 (右上)**: 表現決定薪資，且分配合理
            - **菁英市場 (左上)**: 表現決定薪資，但巨星拿走大部分
            - **平均主義 (右下)**: 薪資分配平均，但與表現無關
            - **混亂市場 (左下)**: 表現與薪資無關，且分配極端
            """)

elif analysis_mode == "公式與變數說明":
    st.markdown('<h2 class="section-title">公式與變數說明</h2>', unsafe_allow_html=True)
    
    # 使用標籤頁組織內容
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["數據來源", "打者指標", "投手指標", "薪資分析", "分析方法", "原創財務指標"])
    
    with tab1:
        st.markdown("""
        ## 數據來源與工具
        
        ### 數據獲取工具
        - **pybaseball**: Python套件，用於獲取MLB官方統計數據
        - **數據年限**: 2023年賽季
        - **資格限制**: 
          - 打者: 至少50個打席 (qual=50)
          - 投手: 至少30局投球 (qual=30)
        
        ### 數據結構
        ```python
        # 主要數據欄位結構
        data = {
            'Name': '球員姓名',
            'Team': '所屬球隊',
            'Position': '守備位置',
            'WAR': '勝場貢獻值',
            'Salary_millions': '薪資（百萬美元）'
        }
        ```
        """)
    
    with tab2:
        st.markdown("""
        ## 打者表現指標
        
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
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **打擊率 (AVG)**
        ```
        AVG = H / AB
        ```
        衡量擊出安打的能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **上壘率 (OBP)**
        ```
        OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
        ```
        衡量上壘能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **長打率 (SLG)**
        ```
        SLG = (1B + 2×2B + 3×3B + 4×HR) / AB
        ```
        衡量長打能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **綜合攻擊指數 (OPS)**
        ```
        OPS = OBP + SLG
        ```
        綜合評估攻擊能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 進階分析指標
        | 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 | 
        |--------|----------|----------|--------------|
        | **WAR** | Wins Above Replacement | 勝場貢獻值 | 衡量球員比替補球員多貢獻多少勝場 | 
        | **wOBA** | Weighted On-Base Average | 加權上壘率 | 考慮不同上壘方式的價值 | 
        | **wRC+** | Weighted Runs Created Plus | 調整後得分創造 | 100為聯盟平均，>100優於平均 | 
        | **OPS+** | Adjusted OPS | 調整後OPS | 考慮球場因素，100為聯盟平均 | 
        """)
    
    with tab3:
        st.markdown("""
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
        """)
    
    with tab4:
        st.markdown("""
        ## 薪資相關變數
        
        ### 主要薪資變數
        | 變數名 | 說明 | 計算公式 |
        |--------|------|----------|
        | **Salary_millions** | 薪資（百萬美元） | 實際薪資除以1,000,000 |
        | **value_ratio** | 性價比 | WAR / salary_in_millions |
        | **salary_percentile** | 薪資百分位 | 薪資在樣本中的百分位排名 |
        | **salary_category** | 薪資級別 | 四分位數分組（低/中低/中高/高） |
        
        ### 性價比計算
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **性價比 (Value Ratio)**
        ```
        value_ratio = WAR / Salary_millions
        ```
        意義：每百萬美元薪資能獲得多少WAR
        - 值越高表示球員越「划算」
        - 值越低表示球員越「昂貴」
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 薪資級別分類
        使用四分位數將球員分為四個薪資級別：
        1. **低薪資**：最低25%的薪資
        2. **中低薪資**：25%-50%的薪資
        3. **中高薪資**：50%-75%的薪資
        4. **高薪資**：最高25%的薪資
        """)
    
    with tab5:
        st.markdown("""
        ## 分析方法
        
        ### 1. 回歸分析
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **線性回歸模型**
        ```
        薪資 = β₀ + β₁ × WAR + ε
        ```
        其中：
        - β₀：截距項（基本薪資）
        - β₁：斜率（每單位WAR的薪資價值）
        - ε：誤差項（市場異常部分）
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 2. 市場異常偵測
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **預期薪資計算**
        ```
        expected_salary = β₀ + β₁ × WAR
        ```
        **薪資殘差計算**
        ```
        salary_residual = actual_salary - expected_salary
        ```
        **差異百分比**
        ```
        residual_percent = (salary_residual / expected_salary) × 100%
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 3. 市場效率指標
        
        #### 相關係數 (Correlation)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **皮爾遜相關係數**
        ```
        r = Σ[(x_i - x̄)(y_i - ȳ)] / √[Σ(x_i - x̄)² Σ(y_i - ȳ)²]
        ```
        範圍：-1 到 1
        - 接近 1：高度正相關
        - 接近 0：無相關
        - 接近 -1：高度負相關
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        #### 決定係數 (R²)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        ```
        R² = 1 - (SS_res / SS_tot)
        ```
        其中：
        - SS_res：殘差平方和
        - SS_tot：總平方和
        意義：模型解釋的變異比例
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 4. 球隊效率分析
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **球隊效率**
        ```
        team_efficiency = total_WAR / total_salary
        ```
        意義：每百萬美元球隊薪資能獲得多少總WAR
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab6:
        st.markdown("""
        ## 原創財務指標 (依據 new_variables.md)
        
        ### 1. 加權綜合價值指數 (WVPI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{WVPI} = w_1 \\times \\text{WAR} + w_2 \\times \\frac{\\text{WAR}}{\\text{Salary}} + w_3 \\times P_{\\text{WAR}} + w_4 \\times (100 - P_{\\text{Salary}}) $$
        
        權重：$w_1=0.35, w_2=0.30, w_3=0.20, w_4=0.15$
        
        意義：多維度球員評估，結合絕對表現、效率、相對排名與成本效益。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 2. 風險調整後價值 (RAV)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{RAV} = \\frac{\\text{WAR} - \\text{WAR}_{\\text{min}}}{\\sigma_{\\text{WAR}} + 1} \\times \\frac{\\text{Median}(\\text{Salary})}{\\text{Salary}} $$
        
        意義：借鑑夏普比率，衡量風險調整後的超額貢獻。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 3. 市場效率殘差指數 (MERI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{MERI}_i = \\frac{\\text{Salary}_i - \\widehat{\\text{Salary}}_i}{\\widehat{\\text{Salary}}_i} \\times \\ln(1 + \\text{WAR}_i) $$
        
        意義：基於迴歸殘差，加入非線性權重，識別市場異常。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 4. 投資組合夏普指數 (PSI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{PSI}_t = \\frac{\\text{WAR}_t^{\\text{team}} - \\text{Salary}_t^{\\text{team}} \\times \\bar{e}_{\\text{league}}}{\\sigma_{\\text{WAR}}^{\\text{team}}} $$
        
        意義：將球隊視為投資組合，評估風險調整後的績效表現。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 5. 雙因子績效矩陣 (TPM)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$
        \\text{Category}(i) = 
        \\begin{cases}
        \\text{明星價值} & \\text{if } Q_{\\text{WAR}} \\geq 50 \\text{ and } Q_{\\text{Value}} \\geq 50 \\\\
        \\text{溢價球星} & \\text{if } Q_{\\text{WAR}} \\geq 50 \\text{ and } Q_{\\text{Value}} < 50 \\\\
        \\text{潛力新秀} & \\text{if } Q_{\\text{WAR}} < 50 \\text{ and } Q_{\\text{Value}} \\geq 50 \\\\
        \\text{球隊冗員} & \\text{if } Q_{\\text{WAR}} < 50 \\text{ and } Q_{\\text{Value}} < 50
        \\end{cases}
        $$
        
        意義：2×2分類矩陣，根據WAR百分位和性價比百分位分類球員。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 6. 同步效率指數 (SEI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{SEI} = \\rho(\\text{WAR}, \\text{Salary}) \\times (1 - G_{\\text{Salary}}) $$
        
        意義：結合市場相關性與分配公平性，總體市場健康指標。
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 頁尾
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6B7280; padding: 1rem 0;">
    <p style="font-size: 0.9rem;">
        MLB薪資市場效率分析專題 | 指導教授: 黃宜侯 | 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)


