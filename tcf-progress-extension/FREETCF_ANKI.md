# FreeTCF 划词进入 Anki

## 日常使用

1. 打开 Anki。
2. 在 FreeTCF 阅读题中拖选一个法语单词。
3. 点击浮出的“查词”。
4. 在法语助手页面确认词义。
5. 点击“加入 Anki · 明天复习”。

卡片会进入：

`French Daily Audio + Reading`

字段来自现有的 `French Chinese English Simple` 模板：

- `French`：词典词头
- `Chinese`：词性、音标与法汉释义
- `English`：留空
- `Sentence`：词典例句、FreeTCF 题目链接、法语助手链接

如果单词已经在 Anki 中，不创建重复卡片，只把原卡安排到明天复习。

## 本机连接

- 学习平台：`127.0.0.1:8765`
- AnkiConnect：`127.0.0.1:8766`
- AnkiConnect 只监听本机。
