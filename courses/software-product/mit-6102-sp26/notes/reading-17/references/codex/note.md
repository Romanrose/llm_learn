# reading-17 · 回调、监听器与事件循环

来源：[MIT 6.102 Spring 2026 · Reading 17: Callbacks and Graphical User Interfaces](https://web.mit.edu/6.102/www/sp26/classes/17-callbacks-guis/)。依据官方阅读正文整理，非课堂逐字稿；下方示例与练习为本地自写教学示例。

> 待审核候选稿 · evidenceMode: reading-only · 尚未人工审核，未登记公开 outputs。

## 核心概念与推理

回调由客户提供而由实现者调用，可以同步也可以异步。Promise 链也是回调组合，回调抛出的异常必须在正确执行上下文处理。GUI 使用监听器模式把事件处理分配给组件，事件队列与循环调度它们。监听器应尽快返回，长时间同步计算会让界面失去响应。监听器间循环通知会产生递归或重复更新，需明确状态所有权和事件方向。

## 具体示例

```ts
button.addEventListener("click", () => {
  status.textContent = "开始";
  void loadData().then(showData, showError);
});
```

监听器立即返回，让事件循环还能处理其他输入。loadData 的拒绝在链内处理；外层同步 try/catch 无法直接捕获以后执行的异步失败。这里要求 showData 与 showError 本身也妥善处理错误。

## 关键机制补充

同步回调的异常沿当前调用栈传播；定时器或事件循环中的异步回调在以后调用栈执行，注册处的 try/catch 不会捕获它。Promise.then 返回新的 Promise，回调返回值决定新的 fulfilled 值，回调抛出或返回拒绝 Promise 则传播失败；若链中继续使用 then，也需继续处理错误。

## 常见误区

认为所有回调都异步；在监听器里忙等；两个监听器互相更新触发无限循环。

## 练习与检查点

设计一个搜索框：输入触发异步检索，说明旧响应晚到时如何避免覆盖新查询结果。

检查答案时必须写清前提、推导和一个反例；仅给出术语名称不足以说明理解。可回到官方文中的 reading exercises 检验，再记录与自己最初判断的差异。

## 原文阅读范围

Timer callbacks, Event loop, Using callbacks with promises, Unpacking an asynchronous function, HTML and the Document Object Model, Input handling, Event sources, Pitfalls in listeners, Summary。

## 资料与边界

完整官方阅读通过上方链接查看；作业、项目及考试见 [软件工程学习入口](/topics/software-engineering/)。官方 [录像说明](https://web.mit.edu/6.102/www/sp26/general/#are_lectures_recorded) 明确：本课不设概念讲授式 lectures，课堂用于主动练习且不录像。概念材料以交互阅读提供，因此本单元不适用课堂逐字稿，也没有生成时间轴。
