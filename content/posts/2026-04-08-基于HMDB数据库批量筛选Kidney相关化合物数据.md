---
title: '基于HMDB数据库批量筛选Kidney相关化合物数据'
url: filter-kidney-related-compounds-from-hmdb-dataset
date: 2026-04-08T21:13:18+08:00
description: 从 HMDB XML 构建 Kidney 相关 HMDB ID 命中集合，再批量过滤 Excel（.xlsx）并导出 CSV，保持原有列结构与顺序不变，同时输出统计与未命中列表。
categories:
  - 编程开发
tags:
  - Python
  - 数据处理
  - 数据筛选
  - 数据可视化
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/filter-kidney-related-compounds-from-hmdb-dataset>  
> 如果您需要远程电脑维修或者编程开发，请[加我微信](https://zhang9.cn)咨询。 

## 背景与目标


目标是把 Excel 里“与肾脏相关（Kidney）”的化合物筛出来，要求：

- 只删除行，不改任何列结构与列顺序
- 支持一个目录下批量处理多个 `.xlsx`
- 输出可追溯（统计信息、未命中列表、汇总文件）

## 核心思路

这类任务最容易踩坑的点是：Excel 行数可能很大，而 XML 也很大，如果每一行都去 XML 里“现查现找”，性能会非常差。

更高效的做法是两步走：

1. **流式解析 XML**：扫描每个 metabolite 的 `tissue_locations` 和 `ontology`，只要文本里包含 `kidney`（大小写不敏感），就把该 metabolite 的主 accession 与 secondary accessions 统一归一化后放进一个 `kidney_hit_set`
2. **过滤 Excel**：遍历每个工作表的每一行，读取 HMDB ID 并做归一化，如果在 `kidney_hit_set` 里就写入 CSV，否则跳过，从而实现“保留命中、删除未命中”

## 代码要点

- **ID 归一化**：支持严格/宽松两种匹配，最终统一成 `HMDB0000123` 这种 7 位格式，避免因为前导 0 或大小写导致误判
- **XML 流式解析**：使用 `lxml.etree.iterparse` 按需扫描并 `elem.clear()` 释放节点，适合超大 XML
- **命中范围更全**：同时检查 `biological_properties/tissue_locations` 里的 tissue 与 `ontology` 的 term
- **保持列结构**：读取 Excel 行时保留原列数，写 CSV 时对齐长度，不会打乱列顺序或丢列
- **批量与多工作表**：同一 `.xlsx` 多个 sheet 会分别输出 CSV（文件名带 sheet 序号和安全化名称）
- **输出可追溯**：会生成 `stats.txt`、`unmatched_hmid.txt` 与目录级 `summary.txt`，方便核对筛选比例和排查漏筛


常用参数：

- `--xlsx-out-suffix .kidney`：输出文件名后缀
- `--xlsx-only a.xlsx,b.xlsx`：只处理指定文件（逗号分隔）
- `--progress-every 5000`：XML 扫描进度输出间隔
- `--xlsx-progress-every 50000`：Excel 行处理进度输出间隔
- `--strict / --no-strict`：严格/宽松 HMDB ID 匹配

## 输出说明

- `*.csv`：过滤后的结果（保留表头 + 命中行），列顺序与原表一致
- `*.unmatched_hmid.txt`：当前文件中出现但未命中的 HMDB ID（去重并排序）
- `*.stats.txt`：行数统计（输入/输出/删除数量、命中/未命中/无效 ID 数量）
- `kidney_filter_summary*.txt`：目录级汇总，便于快速对比每个文件的筛选情况

## 全部代码

```python
import argparse
import csv
import os
import re
import time
from lxml import etree

_DEFAULT_XML_CANDIDATES = (
    r"C:\Users\Administrator\Documents\HMDB离线数据库\hmdb_metabolites\hmdb_metabolites.xml",
    "hmdb_metabolites.xml",
)

_HMDB_ID_RE_STRICT = re.compile(r"^HMDB(\d{1,7})$")
_HMDB_ID_RE_LOOSE = re.compile(r"^HMDB(\d+)$")


def normalize_hmdb_id(raw: str, strict: bool) -> str | None:
    if raw is None:
        return None
    s = raw.strip().upper()
    if not s:
        return None
    m = (_HMDB_ID_RE_STRICT if strict else _HMDB_ID_RE_LOOSE).match(s)
    if not m:
        return None
    digits = m.group(1)
    if strict and len(digits) > 7:
        return None
    if len(digits) > 7:
        return None
    return "HMDB" + digits.zfill(7)


def _tag(ns: str, local: str) -> str:
    return f"{{{ns}}}{local}" if ns else local


def detect_namespace(xml_file: str) -> str:
    with open(xml_file, "rb") as f:
        context = etree.iterparse(f, events=("start",))
        _, root = next(context)
        if "}" in root.tag:
            return root.tag.split("}", 1)[0][1:]
        return ""


def _has_kidney_in_tissues(elem, ns: str) -> bool:
    tissues = elem.find(_tag(ns, "biological_properties"))
    if tissues is None:
        return False
    tissues = tissues.find(_tag(ns, "tissue_locations"))
    if tissues is None:
        return False
    tissue_tag = _tag(ns, "tissue")
    for t in tissues.findall(tissue_tag):
        txt = (t.text or "").strip().casefold()
        if "kidney" in txt:
            return True
    return False


def _has_kidney_in_ontology(elem, ns: str) -> bool:
    ontology = elem.find(_tag(ns, "ontology"))
    if ontology is None:
        return False
    term_tag = _tag(ns, "term")
    for t in ontology.iter(tag=term_tag):
        txt = (t.text or "").strip().casefold()
        if "kidney" in txt:
            return True
    return False


def metabolite_has_kidney(elem, ns: str) -> bool:
    return _has_kidney_in_tissues(elem, ns=ns) or _has_kidney_in_ontology(elem, ns=ns)


def pick_default_xml_path() -> str:
    for p in _DEFAULT_XML_CANDIDATES:
        if os.path.exists(p):
            return p
    return _DEFAULT_XML_CANDIDATES[0]


def build_kidney_hit_set(xml_file: str, strict_id: bool, progress_every: int) -> set[str]:
    ns = detect_namespace(xml_file)
    metabolite_tag = _tag(ns, "metabolite")
    accession_tag = _tag(ns, "accession")
    secondary_accessions_tag = _tag(ns, "secondary_accessions")

    hits: set[str] = set()
    scanned = 0
    start = time.time()

    context = etree.iterparse(xml_file, events=("end",), tag=metabolite_tag)
    for _, elem in context:
        scanned += 1
        if progress_every and scanned % progress_every == 0:
            elapsed = time.time() - start
            rate = scanned / elapsed if elapsed > 0 else 0.0
            print(f"已扫描 {scanned} 条 | Kidney 命中 {len(hits)} 条 | {rate:.1f} 条/秒")

        if metabolite_has_kidney(elem, ns=ns):
            acc_elem = elem.find(accession_tag)
            primary = normalize_hmdb_id((acc_elem.text or "") if acc_elem is not None else "", strict=strict_id)
            if primary:
                hits.add(primary)

            sa_elem = elem.find(secondary_accessions_tag)
            if sa_elem is not None:
                for a in sa_elem.findall(accession_tag):
                    cand = normalize_hmdb_id(a.text or "", strict=strict_id)
                    if cand:
                        hits.add(cand)

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    return hits


def _normalize_header_cell(v) -> str:
    if v is None:
        return ""
    s = str(v).strip().casefold()
    s = s.replace("_", " ").replace("-", " ")
    s = " ".join(s.split())
    return s


def detect_hmdb_id_column(ws) -> int:
    row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
    if not row:
        return 2

    header = [_normalize_header_cell(x) for x in row]
    candidates = ("hmdb id", "hmdbid", "compound id", "compoundid")
    for idx, name in enumerate(header, start=1):
        if name in candidates:
            return idx
    return 2


_INVALID_FILENAME_CHARS_RE = re.compile(r'[\\/:*?"<>|]+')


def _safe_filename_component(s: str) -> str:
    s = (s or "").strip()
    s = _INVALID_FILENAME_CHARS_RE.sub("_", s)
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    s = " ".join(s.split())
    return s[:80] if len(s) > 80 else s


def _row_values_for_csv(src_cells, target_len: int) -> list[str]:
    values = [c.value for c in src_cells]
    if len(values) < target_len:
        values.extend([None] * (target_len - len(values)))

    last_non_none = -1
    for i, v in enumerate(values):
        if v is not None:
            last_non_none = i
    if last_non_none + 1 < target_len:
        for i in range(last_non_none + 1, target_len):
            values[i] = None

    out: list[str] = []
    for v in values:
        if v is None:
            out.append("")
        else:
            out.append(str(v))
    return out


def filter_workbook_keep_kidney_rows(
    src_path: str,
    out_csv_base_path: str,
    xml_file: str,
    kidney_hit_set: set[str],
    strict_id: bool,
    row_progress_every: int,
    unmatched_txt_path: str,
    stats_txt_path: str,
) -> dict[str, int]:
    import openpyxl
    import sqlite3

    in_wb = openpyxl.load_workbook(src_path, read_only=True, data_only=False)

    stats = {"sheets": 0, "rows_in": 0, "rows_out": 0, "rows_removed": 0}
    hmdb_rows_total = 0
    hmdb_rows_hit = 0
    hmdb_rows_miss = 0
    hmdb_rows_invalid = 0
    header_rows = 0

    db_path = out_csv_base_path + ".unmatched.sqlite.tmp"
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute("PRAGMA journal_mode=MEMORY")
        cur.execute("PRAGMA synchronous=OFF")
        cur.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")
        cur.execute("CREATE TABLE IF NOT EXISTS hit (id TEXT PRIMARY KEY)")
        cur.execute("CREATE TABLE IF NOT EXISTS miss (id TEXT PRIMARY KEY)")
        con.commit()

        seen_batch: list[tuple[str]] = []
        hit_batch: list[tuple[str]] = []
        miss_batch: list[tuple[str]] = []
        batch_size = 2000
        out_csv_paths: list[str] = []

        sheetnames = list(in_wb.sheetnames)
        multiple_sheets = len(sheetnames) != 1

        for idx, sheet_name in enumerate(sheetnames, start=1):
            in_ws = in_wb[sheet_name]
            stats["sheets"] += 1

            hmdb_col = detect_hmdb_id_column(in_ws)
            target_len = in_ws.max_column or 0
            sheet_rows_in = 0
            sheet_rows_out = 0
            sheet_rows_removed = 0
            sheet_start = time.time()

            safe_sheet = _safe_filename_component(sheet_name) or f"sheet{idx}"
            if multiple_sheets:
                out_csv_path = f"{out_csv_base_path}.{idx:02d}_{safe_sheet}.csv"
            else:
                out_csv_path = f"{out_csv_base_path}.csv"
            out_csv_paths.append(out_csv_path)

            tmp_csv_path = out_csv_path + ".tmp"
            os.makedirs(os.path.dirname(out_csv_path) or ".", exist_ok=True)
            with open(tmp_csv_path, "w", encoding="utf-8-sig", newline="") as f_csv:
                writer = csv.writer(f_csv, lineterminator="\n")

                print(f"  - Sheet: {sheet_name} | HMDB 列={hmdb_col} | 列数={target_len} | 输出: {os.path.basename(out_csv_path)}")

                first = True
                for row in in_ws.iter_rows(values_only=False):
                    stats["rows_in"] += 1
                    sheet_rows_in += 1
                    if first:
                        writer.writerow(_row_values_for_csv(row, target_len=target_len))
                        stats["rows_out"] += 1
                        sheet_rows_out += 1
                        first = False
                        header_rows += 1
                        continue

                    try:
                        raw_id = row[hmdb_col - 1].value
                    except Exception:
                        raw_id = None

                    if raw_id is None:
                        hmdb_rows_invalid += 1
                        writer.writerow(_row_values_for_csv(row, target_len=target_len))
                        stats["rows_out"] += 1
                        sheet_rows_out += 1
                        continue

                    norm = normalize_hmdb_id(str(raw_id), strict=strict_id)
                    if norm is None:
                        hmdb_rows_invalid += 1
                        writer.writerow(_row_values_for_csv(row, target_len=target_len))
                        stats["rows_out"] += 1
                        sheet_rows_out += 1
                        continue

                    hmdb_rows_total += 1
                    seen_batch.append((norm,))
                    if norm in kidney_hit_set:
                        hmdb_rows_hit += 1
                        hit_batch.append((norm,))
                        writer.writerow(_row_values_for_csv(row, target_len=target_len))
                        stats["rows_out"] += 1
                        sheet_rows_out += 1
                    else:
                        hmdb_rows_miss += 1
                        miss_batch.append((norm,))
                        stats["rows_removed"] += 1
                        sheet_rows_removed += 1

                    if len(seen_batch) >= batch_size:
                        cur.executemany("INSERT OR IGNORE INTO seen(id) VALUES (?)", seen_batch)
                        cur.executemany("INSERT OR IGNORE INTO hit(id) VALUES (?)", hit_batch)
                        cur.executemany("INSERT OR IGNORE INTO miss(id) VALUES (?)", miss_batch)
                        con.commit()
                        seen_batch.clear()
                        hit_batch.clear()
                        miss_batch.clear()

                    if row_progress_every and sheet_rows_in % row_progress_every == 0:
                        elapsed = time.time() - sheet_start
                        rate = sheet_rows_in / elapsed if elapsed > 0 else 0.0
                        print(
                            f"    已处理 {sheet_rows_in} 行 | 保留 {sheet_rows_out} 行 | 删除 {sheet_rows_removed} 行 | {rate:.1f} 行/秒"
                        )

            os.replace(tmp_csv_path, out_csv_path)

        if seen_batch:
            cur.executemany("INSERT OR IGNORE INTO seen(id) VALUES (?)", seen_batch)
            cur.executemany("INSERT OR IGNORE INTO hit(id) VALUES (?)", hit_batch)
            cur.executemany("INSERT OR IGNORE INTO miss(id) VALUES (?)", miss_batch)
            con.commit()

        distinct_total = cur.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
        distinct_hit = cur.execute("SELECT COUNT(*) FROM hit").fetchone()[0]
        distinct_miss = cur.execute("SELECT COUNT(*) FROM miss").fetchone()[0]

        in_wb.close()

        os.makedirs(os.path.dirname(unmatched_txt_path) or ".", exist_ok=True)
        with open(unmatched_txt_path, "w", encoding="utf-8") as f:
            f.write(f"source_xlsx: {os.path.abspath(src_path)}\n")
            f.write(f"xml: {os.path.abspath(xml_file)}\n")
            f.write(f"hmdb_id_distinct_total: {distinct_total}\n")
            f.write(f"hmdb_id_distinct_hit: {distinct_hit}\n")
            f.write(f"hmdb_id_distinct_miss: {distinct_miss}\n")
            f.write("\n")
            for (mid,) in cur.execute("SELECT id FROM miss ORDER BY id"):
                f.write(mid + "\n")

        with open(stats_txt_path, "w", encoding="utf-8") as f:
            f.write(f"source_xlsx: {os.path.abspath(src_path)}\n")
            f.write("output_csv:\n")
            for p in out_csv_paths:
                f.write(f"  - {os.path.abspath(p)}\n")
            f.write(f"unmatched_hmid_txt: {os.path.abspath(unmatched_txt_path)}\n")
            f.write(f"sheets: {stats['sheets']}\n")
            f.write(f"rows_in_total_including_headers: {stats['rows_in']}\n")
            f.write(f"header_rows: {header_rows}\n")
            f.write(f"rows_out_total_including_headers: {stats['rows_out']}\n")
            f.write(f"rows_removed_total: {stats['rows_removed']}\n")
            f.write("\n")
            f.write(f"hmdb_id_rows_total: {hmdb_rows_total}\n")
            f.write(f"hmdb_id_rows_hit: {hmdb_rows_hit}\n")
            f.write(f"hmdb_id_rows_miss: {hmdb_rows_miss}\n")
            f.write(f"hmdb_id_rows_invalid_or_blank: {hmdb_rows_invalid}\n")
            f.write("\n")
            f.write(f"hmdb_id_distinct_total: {distinct_total}\n")
            f.write(f"hmdb_id_distinct_hit: {distinct_hit}\n")
            f.write(f"hmdb_id_distinct_miss: {distinct_miss}\n")
    finally:
        try:
            con.close()
        except Exception:
            pass
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception:
            pass

    return stats


def filter_xlsx_dir(
    xlsx_dir: str,
    xml_file: str,
    strict_id: bool,
    progress_every: int,
    xlsx_row_progress_every: int,
    out_suffix: str,
    only_files: set[str] | None,
) -> None:
    kidney_set = build_kidney_hit_set(xml_file, strict_id=strict_id, progress_every=progress_every)
    print(f"Kidney 命中集合已构建: {len(kidney_set)} 个 HMDB ID")

    summary_path = os.path.join(xlsx_dir, f"kidney_filter_summary{out_suffix}.txt")
    summary_lines: list[str] = []
    summary_lines.append(f"xml: {os.path.abspath(xml_file)}")
    summary_lines.append(f"xlsx_dir: {os.path.abspath(xlsx_dir)}")
    summary_lines.append(f"out_suffix: {out_suffix}")
    summary_lines.append(f"kidney_hit_set_size: {len(kidney_set)}")
    summary_lines.append("")

    for name in sorted(os.listdir(xlsx_dir)):
        if not name.lower().endswith(".xlsx"):
            continue
        if name.lower().endswith(f"{out_suffix.lower()}.xlsx"):
            continue
        if name.lower().endswith(f"{out_suffix.lower()}.csv"):
            continue
        if only_files is not None and name not in only_files:
            continue

        src_path = os.path.join(xlsx_dir, name)
        base = name[:-5]
        out_csv_base = os.path.join(xlsx_dir, f"{base}{out_suffix}")
        unmatched_name = f"{base}{out_suffix}.unmatched_hmid.txt"
        unmatched_path = os.path.join(xlsx_dir, unmatched_name)
        stats_name = f"{base}{out_suffix}.stats.txt"
        stats_path = os.path.join(xlsx_dir, stats_name)

        print(f"处理: {name} -> {base}{out_suffix}.csv")
        file_start = time.time()
        stats = filter_workbook_keep_kidney_rows(
            src_path,
            out_csv_base,
            xml_file,
            kidney_set,
            strict_id=strict_id,
            row_progress_every=xlsx_row_progress_every,
            unmatched_txt_path=unmatched_path,
            stats_txt_path=stats_path,
        )
        elapsed = time.time() - file_start
        print(
            f"完成: sheets={stats['sheets']} rows_in={stats['rows_in']} rows_out={stats['rows_out']} removed={stats['rows_removed']} | {elapsed:.1f}s"
        )
        summary_lines.append(f"file: {name}")
        summary_lines.append(f"  output_csv_base: {os.path.basename(out_csv_base)}")
        summary_lines.append(f"  stats_txt: {stats_name}")
        summary_lines.append(f"  unmatched_hmid_txt: {unmatched_name}")
        summary_lines.append(f"  sheets: {stats['sheets']}")
        summary_lines.append(f"  rows_in: {stats['rows_in']}")
        summary_lines.append(f"  rows_out: {stats['rows_out']}")
        summary_lines.append(f"  rows_removed: {stats['rows_removed']}")
        summary_lines.append("")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", default=pick_default_xml_path())
    parser.add_argument("--xlsx-dir", default="")
    parser.add_argument("--xlsx-out-suffix", default=".kidney")
    parser.add_argument("--xlsx-only", default="")
    parser.add_argument("--strict", action="store_true", default=True)
    parser.add_argument("--no-strict", action="store_false", dest="strict")
    parser.add_argument("--progress-every", type=int, default=5000)
    parser.add_argument("--xlsx-progress-every", type=int, default=50000)
    args = parser.parse_args()

    if not os.path.exists(args.xml):
        raise SystemExit(f"找不到 XML 文件: {args.xml}")

    xlsx_dir = args.xlsx_dir.strip()
    if not xlsx_dir and os.path.isdir("data"):
        xlsx_dir = "data"

    if not xlsx_dir:
        raise SystemExit("未找到可处理的 xlsx 目录。请使用 --xlsx-dir 指定，或在当前目录提供 data 文件夹。")

    if not os.path.isdir(xlsx_dir):
        raise SystemExit(f"找不到 xlsx-dir: {xlsx_dir}")

    try:
        import openpyxl  # noqa: F401
    except Exception as e:
        raise SystemExit(f"缺少依赖 openpyxl，无法处理 xlsx: {e}")

    only_files = None
    if args.xlsx_only.strip():
        only_files = {x.strip() for x in args.xlsx_only.split(",") if x.strip()}

    print(f"XML: {os.path.abspath(args.xml)}")
    print(f"XLSX_DIR: {os.path.abspath(xlsx_dir)}")
    print(f"输出后缀: {args.xlsx_out_suffix}")
    filter_xlsx_dir(
        xlsx_dir=xlsx_dir,
        xml_file=args.xml,
        strict_id=args.strict,
        progress_every=args.progress_every,
        xlsx_row_progress_every=args.xlsx_progress_every,
        out_suffix=args.xlsx_out_suffix,
        only_files=only_files,
    )


if __name__ == "__main__":
    main()

```

## 视频版本

* [哔哩哔哩](https://space.bilibili.com/3546607630944387)
* [YouTube](https://www.youtube.com/@itxiaozhang)


