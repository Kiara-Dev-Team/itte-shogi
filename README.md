# itte-shogi

一手詰め将棋自動生成システム (One-move Checkmate Shogi Puzzle Generator)

Pythonで一手詰め将棋を自動生成するシステムのMVP実装です。

## 特徴

- 一手詰め将棋問題の自動生成
- SFEN形式の完全サポート
- 複数の生成アルゴリズム（ランダム生成、逆算生成）
- 詰み判定と唯一解チェック
- コマンドラインインターフェース

## インストール

```bash
git clone https://github.com/Kiara-Dev-Team/itte-shogi.git
cd itte-shogi
pip install -e .
```

## 使い方

### 問題生成

```bash
# 逆算生成で1問生成
python -m shogi_mate1.cli.main generate --method reverse --n 1

# ランダム生成で3問生成（最大10駒）
python -m shogi_mate1.cli.main generate --method random --n 3 --max-pieces 10

# シード指定で再現可能な生成
python -m shogi_mate1.cli.main generate --method reverse --n 5 --seed 42
```

### 局面の検証

```bash
# SFEN形式の局面を検証
python -m shogi_mate1.cli.main verify --sfen "4k4/3gpg3/9/9/9/9/9/9/4K4 b R 1"
```

### 局面の表示

```bash
# SFEN形式の局面を表示
python -m shogi_mate1.cli.main render --sfen "4k4/9/9/9/9/9/9/9/4K4 b - 1"
```

## プロジェクト構造

```
shogi_mate1/
├── core/          # コアモジュール
│   ├── pieces.py  # 駒の定義
│   ├── board.py   # 盤面データ構造
│   ├── move.py    # 指し手表現
│   ├── attack.py  # 利き計算
│   ├── movegen.py # 合法手生成
│   └── rules.py   # ルール検証
├── solver/        # ソルバーモジュール
│   └── mate1.py   # 一手詰判定
├── gen/           # 生成モジュール
│   ├── random_gen.py  # ランダム生成
│   ├── reverse_gen.py # 逆算生成
│   └── quality.py     # 品質評価
└── cli/           # CLIモジュール
    └── main.py    # コマンドライン処理
```

## 開発

### テスト実行

```bash
pip install pytest
pytest tests/ -v
```

### 技術仕様

- Python 3.10以上
- 型ヒント使用
- 盤面は1次元配列（81要素）で実装
- 駒はintで表現（正: 先手、負: 後手、0: 空）
- SFEN形式に完全対応

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## 参考

- [設計書](https://github.com/Kiara-Dev-Team/itte-shogi/discussions/1)
- [SFEN形式](https://web.archive.org/web/20080131070731/http://www.glaurungchess.com/shogi/usi.html)

