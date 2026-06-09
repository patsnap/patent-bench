#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专利翻译评测指标
支持中翻英（cn2en）和英翻中（en2cn）两个方向。

用法：
    python translation_metrics.py --input your_results.jsonl --direction cn2en
    python translation_metrics.py --input your_results.jsonl --direction en2cn

输入 JSONL 格式要求（在 test_dataset.jsonl 基础上，新增翻译结果字段）：
    中翻英：新增 content_cn_translate 字段
    英翻中：新增 content_en_translate 字段
"""

import argparse
import json
import re
import sys
from pathlib import Path

import jieba
import nltk
import sacrebleu
import spacy
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from rouge import Rouge

nltk.download("wordnet", quiet=True)
nltk.download("omw", quiet=True)

sys.setrecursionlimit(10000)

nlp = spacy.load("en_core_web_sm")
rouge = Rouge()


# ---------------------------------------------------------------------------
# 预处理
# ---------------------------------------------------------------------------

def get_lemma(text):
    if isinstance(text, list):
        return [get_lemma(t) for t in text]
    doc = nlp(str(text))
    return " ".join(token.lemma_.lower() for token in doc)


def segment_zh(text):
    return " ".join(jieba.cut(str(text)))


# ---------------------------------------------------------------------------
# 单条指标计算
# ---------------------------------------------------------------------------

class TranslationScorer:

    # ---- 中翻英 ----

    @staticmethod
    def bleu1_cn2en(row):
        ref = row["content_en"].split()
        hyp = row["response"].split()
        return sentence_bleu([ref], hyp, weights=(1, 0, 0, 0))

    @staticmethod
    def bleu2_cn2en(row):
        ref = row["content_en"].split()
        hyp = row["response"].split()
        return sentence_bleu([ref], hyp, weights=(0.5, 0.5, 0, 0))

    @staticmethod
    def bleu4_cn2en(row):
        ref = row["content_en"].split()
        hyp = row["response"].split()
        return sentence_bleu([ref], hyp, weights=(0.25, 0.25, 0.25, 0.25))

    @staticmethod
    def sacrebleu_cn2en(row):
        bleu = sacrebleu.corpus_bleu([row["response"]], [[row["content_en"]]])
        return bleu.score / 100

    @staticmethod
    def meteor_cn2en(row):
        return meteor_score([row["content_en"].split()], row["response"].split())

    @staticmethod
    def rouge1_cn2en(row):
        scores = rouge.get_scores(row["response"], row["content_en"])
        return scores[0]["rouge-1"]["f"]

    @staticmethod
    def rouge2_cn2en(row):
        scores = rouge.get_scores(row["response"], row["content_en"])
        return scores[0]["rouge-2"]["f"]

    @staticmethod
    def rougel_cn2en(row):
        scores = rouge.get_scores(row["response"], row["content_en"])
        return scores[0]["rouge-l"]["f"]

    # ---- 英翻中 ----

    @staticmethod
    def bleu1_en2cn(row):
        ref = list(jieba.cut(row["content_cn"]))
        hyp = list(jieba.cut(row["response"]))
        return sentence_bleu([ref], hyp, weights=(1, 0, 0, 0))

    @staticmethod
    def bleu2_en2cn(row):
        ref = list(jieba.cut(row["content_cn"]))
        hyp = list(jieba.cut(row["response"]))
        return sentence_bleu([ref], hyp, weights=(0.5, 0.5, 0, 0))

    @staticmethod
    def bleu4_en2cn(row):
        ref = list(jieba.cut(row["content_cn"]))
        hyp = list(jieba.cut(row["response"]))
        return sentence_bleu([ref], hyp, weights=(0.25, 0.25, 0.25, 0.25))

    @staticmethod
    def sacrebleu_en2cn(row):
        bleu = sacrebleu.corpus_bleu([row["response"]], [[row["content_cn"]]], tokenize="zh")
        return bleu.score / 100

    @staticmethod
    def meteor_en2cn(row):
        ref = list(jieba.cut(row["content_cn"]))
        hyp = list(jieba.cut(row["response"]))
        return meteor_score([ref], hyp)

    @staticmethod
    def rouge1_en2cn(row):
        scores = rouge.get_scores(segment_zh(row["response"]), segment_zh(row["content_cn"]))
        return scores[0]["rouge-1"]["f"]

    @staticmethod
    def rouge2_en2cn(row):
        scores = rouge.get_scores(segment_zh(row["response"]), segment_zh(row["content_cn"]))
        return scores[0]["rouge-2"]["f"]

    @staticmethod
    def rougel_en2cn(row):
        scores = rouge.get_scores(segment_zh(row["response"]), segment_zh(row["content_cn"]))
        return scores[0]["rouge-l"]["f"]

    # ---- 通用 ----

    @staticmethod
    def length_metrics_cn2en(row):
        ref_len = len(str(row["content_en"]).split())
        hyp_len = len(str(row["response"]).split())
        ratio = hyp_len / ref_len if ref_len > 0 else 0
        has_zh = bool(re.search(r"[一-鿿]", str(row["raw_response"])))
        return {
            "content_length": ref_len,
            "response_length": hyp_len,
            "length_ratio": ratio,
            "hallucination": 1 if (ratio > 5 or has_zh) else 0,
            "miss_translation": 1 if ratio < 0.5 else 0,
        }

    @staticmethod
    def length_metrics_en2cn(row):
        ref_len = len(str(row["content_cn"]))
        hyp_len = len(str(row["raw_response"]))
        ratio = hyp_len / ref_len if ref_len > 0 else 0
        has_en = bool(re.search(r"[a-zA-Z]", str(row["raw_response"])))
        ref_has_en = bool(re.search(r"[a-zA-Z]", str(row["content_cn"])))
        return {
            "content_length": ref_len,
            "response_length": hyp_len,
            "length_ratio": ratio,
            "hallucination": 1 if (ratio > 5 or (has_en and not ref_has_en)) else 0,
            "miss_translation": 1 if ratio < 0.5 else 0,
        }

    # ---- 专业性指标 ----

    @staticmethod
    def check_term_presence(row, term_field):
        return 1 if row[term_field] in row["response"] else 0

    @staticmethod
    def check_term_consistency(row, term_field):
        return 1 if row["response"].count(row[term_field]) >= 2 else 0

    @staticmethod
    def check_patent_norm(row, term_field):
        phrases = row[term_field]
        if not isinstance(phrases, list):
            return 0
        results = [1 if p.lower() in row["response"] else 0 for p in phrases]
        return round(sum(results) / len(results), 2) if results else 0

    @staticmethod
    def check_special_statement(row, term_field):
        words = row["response"].split()
        word_list = row[term_field]
        return 0 if any(w in word_list for w in words) else 1


# ---------------------------------------------------------------------------
# 主评测流程
# ---------------------------------------------------------------------------

NORMAL_LABELS = {"normal_sentence", "normal_character", "paragraph_accuracy", "special_sentence", "document_accuracy"}
VERTICAL_LABELS = {"special_character", "terminology_accuracy", "terminology_consistency", "patent_writing_norm"}


def _score_row_cn2en(row):
    label2 = row.get("label_2", "")
    if label2 in NORMAL_LABELS:
        if label2 == "document_accuracy":
            return TranslationScorer.sacrebleu_cn2en(row)
        return (TranslationScorer.bleu1_cn2en(row) + TranslationScorer.meteor_cn2en(row)) / 2
    if label2 == "special_character":
        return TranslationScorer.check_term_presence(row, "special_en")
    if label2 == "terminology_accuracy":
        return TranslationScorer.check_term_presence(row, "special_en")
    if label2 == "terminology_consistency":
        return TranslationScorer.check_term_consistency(row, "special_en")
    if label2 == "patent_writing_norm":
        return TranslationScorer.check_patent_norm(row, "special_en")
    if label2 == "special_sentence":
        return TranslationScorer.check_special_statement(row, "special_en")
    return None


def _score_row_en2cn(row):
    label2 = row.get("label_2", "")
    if label2 in NORMAL_LABELS:
        if label2 == "document_accuracy":
            return TranslationScorer.sacrebleu_en2cn(row)
        return (TranslationScorer.rouge1_en2cn(row) + TranslationScorer.meteor_en2cn(row)) / 2
    if label2 == "special_character":
        return TranslationScorer.check_term_presence(row, "special_cn")
    if label2 == "terminology_accuracy":
        return TranslationScorer.check_term_presence(row, "special_cn")
    if label2 == "terminology_consistency":
        return TranslationScorer.check_term_consistency(row, "special_cn")
    if label2 == "patent_writing_norm":
        return TranslationScorer.check_patent_norm(row, "special_cn")
    if label2 == "special_sentence":
        return TranslationScorer.check_special_statement(row, "special_cn")
    return None


def evaluate(input_path: str, direction: str) -> dict:
    """
    读取带翻译结果的 JSONL，计算所有指标，返回汇总 dict。

    direction: "cn2en" 或 "en2cn"
    """
    assert direction in ("cn2en", "en2cn"), "direction 必须是 cn2en 或 en2cn"
    translate_field = "content_cn_translate" if direction == "cn2en" else "content_en_translate"

    rows = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    scorer = TranslationScorer()
    results = []

    for row in rows:
        if translate_field not in row:
            continue
        row["response"] = row[translate_field]
        raw_response = row["response"]  # 保存原始译文用于幻觉检测

        # 词形还原（cn2en 对英文做 lemma，en2cn 对中文 response 不做 lemma，仅对英文 special 做 lemma）
        if direction == "cn2en":
            row["response"] = get_lemma(row["response"])
            row["content_en"] = get_lemma(row["content_en"])
            if row.get("special_en") and row["special_en"] != "Zero":
                row["special_en"] = get_lemma(row["special_en"])
        else:
            if row.get("special_en") and row["special_en"] != "Zero":
                row["special_en"] = get_lemma(row["special_en"])

        row["raw_response"] = raw_response

        label2 = row.get("label_2", "")

        metrics = {}
        if direction == "cn2en":
            if label2 in NORMAL_LABELS:
                metrics["bleu_1"] = scorer.bleu1_cn2en(row)
                metrics["meteor"] = scorer.meteor_cn2en(row)
                lm = scorer.length_metrics_cn2en(row)
                metrics.update(lm)
                score = scorer.sacrebleu_cn2en(row) if label2 == "document_accuracy" else (metrics["bleu_1"] + metrics["meteor"]) / 2
            else:
                score = _score_row_cn2en(row)
        else:
            if label2 in NORMAL_LABELS:
                metrics["rouge_1"] = scorer.rouge1_en2cn(row)
                metrics["meteor"] = scorer.meteor_en2cn(row)
                lm = scorer.length_metrics_en2cn(row)
                metrics.update(lm)
                score = scorer.sacrebleu_en2cn(row) if label2 == "document_accuracy" else (metrics["rouge_1"] + metrics["meteor"]) / 2
            else:
                score = _score_row_en2cn(row)

        if score is not None:
            metrics["score"] = score
        metrics["label_2"] = label2
        metrics["pn"] = row.get("pn", "")
        results.append(metrics)

    # 汇总
    from collections import defaultdict
    label_scores: dict = defaultdict(list)
    label_hallucination: dict = defaultdict(list)
    label_miss: dict = defaultdict(list)

    for r in results:
        if "score" in r:
            label_scores[r["label_2"]].append(r["score"])
        if "hallucination" in r:
            label_hallucination[r["label_2"]].append(r["hallucination"])
        if "miss_translation" in r:
            label_miss[r["label_2"]].append(r["miss_translation"])

    summary = {
        "direction": direction,
        "total": len(results),
        "accuracy_by_label": {
            k: round(sum(v) / len(v) * 100, 2) for k, v in label_scores.items()
        },
        "hallucination_pct_by_label": {
            k: round(sum(v) / len(v) * 100, 2) for k, v in label_hallucination.items()
        },
        "miss_translation_pct_by_label": {
            k: round(sum(v) / len(v) * 100, 2) for k, v in label_miss.items()
        },
    }
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="专利翻译评测指标计算")
    parser.add_argument("--input", required=True, help="带翻译结果的 JSONL 文件路径")
    parser.add_argument(
        "--direction",
        required=True,
        choices=["cn2en", "en2cn"],
        help="翻译方向：cn2en（中翻英）或 en2cn（英翻中）",
    )
    parser.add_argument("--output", default=None, help="结果输出 JSON 路径（可选）")
    args = parser.parse_args()

    summary = evaluate(args.input, args.direction)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\n结果已写入 {args.output}")


if __name__ == "__main__":
    main()
