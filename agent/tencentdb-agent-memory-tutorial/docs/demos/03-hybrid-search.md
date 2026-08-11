# Demo 3：BM25 + 向量 + RRF

源码位置：`examples/hybrid/index.ts`。

## 为什么要融合两个排序？

关键词排序擅长精确词，向量排序擅长语义。真实项目里两者的分数也不一定在同一量纲，所以不要直接相加；先各自取排名，再用 RRF 融合。

## 运行

```bash
npm run demo:hybrid
```

输出中会看到同一条记录同时出现在两个列表时分数更高。

## 加分练习：实现一个词法检索器

可以从下面的评分开始：

```ts
function lexicalScore(query: string, document: string) {
  const q = new Set(query.toLowerCase().split(/\s+/))
  const d = new Set(document.toLowerCase().split(/\s+/))
  return [...q].filter((word) => d.has(word)).length / Math.max(q.size, 1)
}
```

中文场景需要分词或字符 n-gram；官方实现使用本地 BM25 编码器，并支持中文语言配置。教学版最终项目使用简单 token/n-gram，目的是展示接口和预算，而不是替代成熟检索库。
