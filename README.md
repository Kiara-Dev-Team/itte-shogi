# itte-shogi

一手詰め将棋自動生成システム (One-move Checkmate Shogi Puzzle Generator)

Pythonで一手詰め将棋を自動生成するシステムのMVP実装です。

## 特徴

- 一手詰め将棋問題の自動生成
- **ユーザー作成パズルのサポート** - 自分のパズルを作成、保存、テスト
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

### ユーザーパズルの作成

独自の一手詰めパズルを作成して保存できます：

```bash
# インタラクティブモード - 対話形式で作成
python -m shogi_mate1.cli.main create

# バッチモード - すべてのパラメータを指定
python -m shogi_mate1.cli.main create \
  --sfen "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1" \
  --name "My Corner Mate" \
  --description "A mate in the corner" \
  --author "YourName" \
  --tags beginner corner \
  --batch

# 検証失敗でも強制保存（テスト用）
python -m shogi_mate1.cli.main create \
  --sfen "YOUR_SFEN_HERE" \
  --force \
  --batch
```

**パズル作成時のバリデーション：**
- SFEN形式の妥当性チェック
- 一手詰め判定
- 唯一解チェック
- 詰み手の表示

### 保存したパズルのテスト

```bash
# すべての保存済みパズルをテスト
python -m shogi_mate1.cli.main test

# 詳細表示付きでテスト
python -m shogi_mate1.cli.main test --verbose

# 特定のパズルのみテスト（インデックス指定）
python -m shogi_mate1.cli.main test --index 0
```

### 保存したパズルの一覧表示

```bash
# パズル一覧を表示
python -m shogi_mate1.cli.main list

# SFEN含む詳細情報を表示
python -m shogi_mate1.cli.main list --verbose
```

### 局面の検証

```bash
# SFEN形式の局面を検証
python -m shogi_mate1.cli.main verify --sfen "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1"
```

### 局面の表示

```bash
# SFEN形式の局面を表示
python -m shogi_mate1.cli.main render --sfen "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1"
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
├── puzzles/       # パズル管理モジュール
│   └── storage.py # パズル保存・読込
└── cli/           # CLIモジュール
    └── main.py    # コマンドライン処理
```

## パズルストレージ

作成したパズルは `./puzzles/user_puzzles.json` に JSON 形式で保存されます。

### パズルファイル形式

```json
{
  "sfen": "7gk/7pg/8R/9/9/9/9/9/4K4 b - 1",
  "name": "Corner Mate Example",
  "description": "A mate in the corner position",
  "author": "YourName",
  "tags": ["beginner", "corner"],
  "created_at": "2026-01-06T00:00:00"
}
```

## 例題

`examples/` ディレクトリに例題とSFEN形式の詳しい説明があります：

```bash
# 例題の使い方を見る
cat examples/README.md

# 例題をコピーしてテスト
cp examples/example_puzzles.json puzzles/user_puzzles.json
python -m shogi_mate1.cli.main test
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
- [例題とチュートリアル](examples/README.md)

