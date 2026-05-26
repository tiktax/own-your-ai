# own-your-ai

> あなたのAI。あなたのデータ。あなたのルール。

**#MyAI #DigitalSovereignty #3rdWayAI**

---

## ビジョン

AIシステムは今や個人の意思決定——健康・金融・人間関係・アイデンティティ——を仲介するようになっている。しかしそのAIが動作するインフラのほぼすべては外部にある: クラウドプロバイダー、プラットフォーム事業者、サードパーティのモデルホスト。

**own-your-ai** は第三の道だ: プラットフォームのAIでも企業のAIでもなく、あなたのハードウェアで動き、あなたのルールによって管理され、あなたのデータが決して外に出ないAI。

[MyData Global](https://www.mydata.org/) の原則に沿い、AIレイヤーをコードとして実装することで差別化する。

---

## 設計原則

| 原則 | 意味 |
|---|---|
| **オフラインファースト** | 推論はすべてローカルで完結。デフォルトでデータはデバイス外に送出しない。 |
| **個人がIdP** | あなた自身がアイデンティティ・認証情報・同意判断を管理する。 |
| **SSI/DID基盤** | 可搬・検証可能なアイデンティティ——いかなるプラットフォームにも所有されない。 |
| **データポータビリティ** | AIの全履歴はいつでもオープン形式でエクスポート可能。 |
| **暗号による説明責任** | すべてのAI判断は署名・監査可能——あなたによって、あなたのために。 |

---

## 技術的基盤

本プロジェクトは [ai-infra-portfolio](https://github.com/tiktax/ai-infra-portfolio) の暗号プリミティブを継承する:

| コンポーネント | 役割 |
|---|---|
| ECDSA P-256 + ハッシュチェーン（Phase 5）| 個人のAI判断に対する監査証跡 |
| ポスト量子署名——ML-DSA-65（Phase 5）| 将来対応のアイデンティティ基盤 |
| PIIガード + 表示時スクラブ（Phase 6a）| デバイスレベルのプライバシー強制 |

---

## 法的フレームワーク

| 管轄 | 適用法令 | 対応する権利 |
|---|---|---|
| EU | AI Act（第22条）+ GDPR（第17・20条）| 説明を受ける権利 + データポータビリティ権 |
| 米国 | EO 14110 + 各州AIビル | 透明性・オプトアウト権 |
| 日本 | 改正個人情報保護法（2022）+ AI事業者ガイドライン | 要配慮個人情報 + 利用停止権 |

---

## 計画する主要機能

- **モバイルLLM**: Gemma3クラスのモデルがオンデバイスで完全動作（現時点で技術的に実現可能）
- **ソーシャルリカバリー**: M-of-Nによるアイデンティティキー回復——中央集権的権限は不要
- **SSI/DIDクレデンシャル**: 自己主権型アイデンティティクレデンシャルの発行・検証
- **個人AI監査ログ**: 可搬・署名済み・ユーザー所有のAI判断記録

---

## 設計上の制約

- **UX形態は未定**: 現時点ではスマートフォンが主要ターゲットだが、時代が決めるUX形態に縛られないアーキテクチャとする
- **日本の法的ギャップ**: 日本のAIガバナンスフレームワークは3管轄の中で最も曖昧で、日本固有の実装における既知のブロッカー
- **スコープ**: 本プロジェクトはAIレイヤーを実装する。MyData Globalのデータ共有合意書や同意管理プロトコルの作業は重複しない

---

## ai-infra-portfolio との関係

| プロジェクト | スコープ | 対象ユーザー |
|---|---|---|
| [ai-infra-portfolio](https://github.com/tiktax/ai-infra-portfolio) | 組織のAIガバナンス | チーム・コンプライアンス担当・CISO |
| **own-your-ai** | 個人のAI主権 | すべての人 |

組織向けに構築したガバナンス基本要素（署名付き監査証跡・プライバシー強制・ITSM準拠変更管理）は、個人にとっても正しい基本要素だ——外ではなく内側に向けるだけ。

---

## タグ

`#MyAI` `#DigitalSovereignty` `#3rdWayAI` `#SSI` `#DID` `#MyDataGlobal` `#OfflineAI` `#PersonalAI`

---

## ステータス — Phase 1: Foundation ✅

暗号スケルトンがエンドツーエンドで動作する:

```bash
pip install -e ".[dev]"

oya init                              # human/ai 鍵ペア生成
oya sign -m "hello world" --as human  # ~/.ownyourai/audit.jsonl に署名エントリ追加
oya audit list                        # ログ確認
oya verify                            # ECDSA + ハッシュチェーン整合性チェック
oya export                            # GDPR 第20条 ポータブル JSON 出力
```

**次のフェーズ**: [docs/roadmap.md](docs/roadmap.md) 参照。Phase 2 はパスフレーズ暗号化鍵 + macOS Keychain 統合、Phase 3 で `oya` をオンデバイス LLM に接続。

**ドキュメント**:
- [docs/architecture.md](docs/architecture.md) — 5レイヤー設計
- [docs/threat-model.md](docs/threat-model.md) — 個人スケール STRIDE
- [docs/legal-matrix.md](docs/legal-matrix.md) — EU AI Act / GDPR / CCPA / 改正個情法 マッピング
- [docs/decisions/](docs/decisions/) — ADR 群

**[ai-infra-portfolio](https://github.com/tiktax/ai-infra-portfolio) との関係**: 本プロジェクトはその Phase 8 — 同じガバナンス基盤を、組織ではなく個人に向ける。
