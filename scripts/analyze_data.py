import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

CK_ALL_CSV = "data/all_repos_metrics.csv"
TOP1000_CSV = "data/top1000_java_repos.csv"
RESULTS_DIR = "results"
REPO_LEVEL_CSV = os.path.join(RESULTS_DIR, "repo_level_metrics.csv")
STATS_SUMMARY_CSV = os.path.join(RESULTS_DIR, "stats_summary.csv")

def normalize_repo_name(name):
    if pd.isna(name):
        return ""
    n = str(name).strip()
    n = n.replace("/", "_")
    n = re.sub(r'[\'"]', "", n)
    return n

def compute_age_years(created_at):
    try:
        dt = pd.to_datetime(created_at)
        now = pd.Timestamp.now()
        delta = now - dt
        return delta.days / 365.25
    except Exception:
        return np.nan

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    df_classes = pd.read_csv(CK_ALL_CSV, low_memory=False)
    df_top = pd.read_csv(TOP1000_CSV, low_memory=False)

    name_cols = [c for c in df_top.columns if c.lower() in ("namewithowner", "name_with_owner", "name")]
    repo_col_top = name_cols[0] if len(name_cols) >= 1 else df_top.columns[0]
    df_top["repo_key"] = df_top[repo_col_top].apply(normalize_repo_name)

    if "repo_name" in df_classes.columns:
        df_classes["repo_key"] = df_classes["repo_name"].apply(normalize_repo_name)
    else:
        if "filename" in df_classes.columns:
            df_classes["repo_key"] = df_classes["filename"].apply(lambda x: normalize_repo_name(x.split("/")[0]) if isinstance(x, str) else "")
        else:
            df_classes["repo_key"] = ""

    lower_cols = {c.lower(): c for c in df_classes.columns}
    def col_name(preferred):
        return lower_cols.get(preferred.lower(), None)

    cols_map = {
        "cbo": col_name("cbo") or "cbo",
        "dit": col_name("dit") or "dit",
        "lcom": col_name("lcom") or "lcom",
        "loc": col_name("loc") or "loc",
        "wmc": col_name("wmc") or "wmc"
    }

    for k, v in cols_map.items():
        if v not in df_classes.columns:
            df_classes[v] = np.nan

    for v in cols_map.values():
        df_classes[v] = pd.to_numeric(df_classes[v], errors="coerce")

    agg_funcs = {
        cols_map["cbo"]: ["mean", "median", "std"],
        cols_map["dit"]: ["mean", "median", "std"],
        cols_map["lcom"]: ["mean", "median", "std"],
        cols_map["loc"]: ["sum", "mean", "median"],
        cols_map["wmc"]: ["mean", "median"]
    }

    df_agg = df_classes.groupby("repo_key").agg(agg_funcs)
    df_agg.columns = ["_".join(filter(None, map(str, col))).strip() for col in df_agg.columns.values]
    df_agg = df_agg.reset_index().rename(columns={"repo_key": "repo_key"})
    class_counts = df_classes.groupby("repo_key").size().reset_index(name="num_classes")
    df_agg = df_agg.merge(class_counts, on="repo_key", how="left")

    cand_map = {}
    for c in df_top.columns:
        lc = c.lower()
        if "star" in lc:
            cand_map["stars"] = c
        if "created" in lc:
            cand_map["created_at"] = c
        if "pushed" in lc or "updated" in lc:
            cand_map["pushed_at"] = c
        if "disk" in lc:
            cand_map["disk_usage"] = c
        if "fork" in lc:
            cand_map["forks"] = c
        if "url" in lc:
            cand_map["url"] = c

    df_top_small = df_top[["repo_key"] + [v for v in cand_map.values() if v in df_top.columns]].copy()

    if "created_at" in df_top_small.columns:
        df_top_small["age_years"] = df_top_small["created_at"].apply(compute_age_years)
    else:
        df_top_small["age_years"] = np.nan

    if "stars" in df_top_small.columns:
        df_top_small["stars"] = pd.to_numeric(df_top_small["stars"], errors="coerce")
    else:
        df_top_small["stars"] = np.nan

    df_repo = df_agg.merge(df_top_small, on="repo_key", how="left")
    df_repo.to_csv(REPO_LEVEL_CSV, index=False)
    stats = df_repo.describe(include=[np.number]).transpose()
    stats.to_csv(STATS_SUMMARY_CSV)

    if "age_years" in df_repo.columns:
        plt.figure()
        sns.histplot(df_repo["age_years"].dropna(), bins=30, kde=False)
        plt.xlabel("Idade (anos)")
        plt.title("Distribuição da Idade dos Repositórios")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "plot_hist_age.png"))
        plt.close()

    if "stars" in df_repo.columns and df_repo["stars"].notna().sum() > 0:
        plt.figure()
        sns.histplot(df_repo["stars"].dropna(), bins=50, log_scale=(False, True))
        plt.xlabel("Stars")
        plt.title("Distribuição de Stars")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "plot_hist_stars.png"))
        plt.close()

    if "stars" in df_repo.columns and df_repo["stars"].notna().sum() > 0 and (cols_map["lcom"] + "_median") in df_repo.columns:
        tmp = df_repo[[cols_map["lcom"] + "_median", "stars"]].dropna()
        if tmp["stars"].nunique() > 1:
            tmp["star_quantile"] = pd.qcut(tmp["stars"], q=4, labels=["Q1","Q2","Q3","Q4"], duplicates="drop")
            plt.figure()
            sns.boxplot(x="star_quantile", y=cols_map["lcom"] + "_median", data=tmp)
            plt.xlabel("Quartil de Popularidade (stars)")
            plt.ylabel("LCOM (mediana)")
            plt.title("LCOM por Quartil de Popularidade")
            plt.tight_layout()
            plt.savefig(os.path.join(RESULTS_DIR, "plot_box_lcom_by_pop.png"))
            plt.close()

    if "stars" in df_repo.columns and df_repo["stars"].notna().sum() > 0 and (cols_map["lcom"] + "_median") in df_repo.columns:
        plt.figure()
        sns.regplot(x="stars", y=cols_map["lcom"] + "_median", data=df_repo.dropna(subset=["stars", cols_map["lcom"] + "_median"]), scatter_kws={"s": 20}, lowess=True)
        plt.xscale("log")
        plt.xlabel("Stars (log)")
        plt.ylabel("LCOM (mediana)")
        plt.title("Relação entre Stars e LCOM")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "plot_scatter_stars_vs_lcom.png"))
        plt.close()

    loc_sum_col = cols_map["loc"] + "_sum"
    dit_med_col = cols_map["dit"] + "_median"
    if loc_sum_col in df_repo.columns and dit_med_col in df_repo.columns:
        plt.figure()
        sns.regplot(x=loc_sum_col, y=dit_med_col, data=df_repo.dropna(subset=[loc_sum_col, dit_med_col]), scatter_kws={"s": 20})
        plt.xscale("log")
        plt.xlabel("LOC (soma, log)")
        plt.ylabel("DIT (mediana)")
        plt.title("Relação entre LOC e DIT")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "plot_scatter_loc_vs_dit.png"))
        plt.close()

    num_cols = df_repo.select_dtypes(include=[np.number])
    if not num_cols.empty:
        corr = num_cols.corr(method="spearman")
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0)
        plt.title("Mapa de Correlação")
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "plot_heatmap_correlations.png"))
        plt.close()

if __name__ == "__main__":
    main()
