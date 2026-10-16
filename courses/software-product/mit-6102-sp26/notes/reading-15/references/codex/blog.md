# 代码像同步执行，并不代表世界停下来

来源：[MIT 6.102 Spring 2026 · Reading 15: Promises](https://web.mit.edu/6.102/www/sp26/classes/15-promises/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 从一个具体问题开始

async/await 让下载代码容易阅读，但在等待第一个响应时，其他事件仍可修改页面状态。返回之后读取的字段未必与等待前相同，顺序外观隐藏了并发边界。

## 看清问题背后的结构

Promise 表示一个可能尚未完成的计算结果，成功与拒绝都必须纳入控制流。async 函数返回 Promise，await 暂停当前异步执行并在完成后继续，它不忙等也不阻塞整个事件循环。先启动多个独立操作再聚合，才能让它们重叠；循环里逐个 await 则串行等待。Promise.all 要求全部成功，any 等待首个成功，race 等待首个结算。聚合完成并不自动取消剩余操作。

## 用一个小例子检验理解

```ts
const pa = fetch("https://example.org/a");
const pb = fetch("https://example.org/b");
const [a,b] = await Promise.all([pa,pb]);
```

两个 fetch 在等待之前都已启动。若先 await 第一个 fetch 再调用第二个，网络等待会串行。all 的拒绝需处理，且任一失败不会自动撤销另一个请求。

## 关键机制补充

Promise 是未来结算结果的容器，并不承诺背后存在独立线程或后台任务；构造器执行器会同步运行，fetch 等 API 才启动相应异步工作。async 函数会把同步返回包装为 fulfilled Promise，把抛出的异常变成 rejected Promise。try/catch 只有在其作用域内 await 或返回链的 catch 才能处理后续拒绝；void 丢弃返回值不会处理拒绝。

## 把概念放回工程决策

让函数签名清楚传递 Promise，明确并行与依赖关系，并把拒绝当作正常设计分支。await 既是获取结果，也是交出控制的地方。

容易走偏的地方是：忘记 await 而把 Promise 当结果；认为 await 冻结共享状态；把 Promise.all 当取消机制。这些问题不能通过记住一个术语自动解决，需要用具体调用者、输入和状态来检查。

## 亲手做一次

比较顺序 await 与 Promise.all 的依赖图，说明第一个请求失败时两种写法分别启动了哪些任务。

先独立写下判断，再对照官方阅读；这篇文章是阅读解释和练习入口，未包含原课堂的互动、时间轴或未公开内容。

## 自写例子：拒绝传播

```ts
async function readName(): Promise<string> {
  try {
    const response = await fetch("https://example.org/name");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.text();
  } catch (error) {
    // 记录后重新抛出，调用方仍负责处理失败
    throw error;
  }
}
```

fetch 不会仅因 HTTP 404 自动拒绝，必须检查响应状态。response.text() 本身也返回 Promise，示例用 return await 使读取正文的失败仍进入本函数 catch；若直接 return response.text()，该异步拒绝不会被这里的 catch 捕获。示例不保证取消，也没有把日志当作恢复。
