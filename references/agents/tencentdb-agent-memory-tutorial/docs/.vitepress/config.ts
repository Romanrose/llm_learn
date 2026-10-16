import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  lang: 'zh-CN',
  title: 'Agent Memory 从零到一',
  description: '以 TencentDB-Agent-Memory 为参考，手把手实现一个可运行的 Agent Memory。',
  cleanUrls: true,
  themeConfig: {
    logo: '🧠',
    nav: [
      { text: '首页', link: '/' },
      { text: '教程主线', link: '/guide/01-why-memory' },
      { text: '渐进式 Demo', link: '/demos/01-basic-memory' },
      { text: '教学版源码', link: '/guide/09-final-project' },
      { text: '参考仓库', link: 'https://github.com/TencentCloud/TencentDB-Agent-Memory' },
    ],
    sidebar: {
      '/guide/': [
        {
          text: '一、先建立心智模型',
          items: [
            { text: '1. 为什么 Agent 需要 Memory', link: '/guide/01-why-memory' },
            { text: '2. 四层记忆模型：L0 → L3', link: '/guide/02-four-layers' },
            { text: '3. 官方架构：Core、Adapter 与 Gateway', link: '/guide/03-architecture' },
          ],
        },
        {
          text: '二、拆解关键机制',
          items: [
            { text: '4. L0：安全地捕获原始对话', link: '/guide/04-capture' },
            { text: '5. L1：从对话提取原子记忆', link: '/guide/05-extraction' },
            { text: '6. 召回：混合检索与渐进式披露', link: '/guide/06-recall' },
            { text: '7. 短期记忆：外置上下文与 Mermaid 符号图', link: '/guide/07-offload' },
            { text: '8. 生产化链路：Pipeline、Hook 与 API', link: '/guide/08-production-chain' },
          ],
        },
        {
          text: '三、完成教学版项目',
          items: [
            { text: '9. 最终项目：Tiny Memory', link: '/guide/09-final-project' },
            { text: '10. 运行、调试与验证', link: '/guide/10-run-and-debug' },
            { text: '11. 从教学版走向生产', link: '/guide/11-extensions' },
          ],
        },
      ],
      '/demos/': [
        { text: 'Demo 1：内存中的记忆本', link: '/demos/01-basic-memory' },
        { text: 'Demo 2：四层记忆与提取器', link: '/demos/02-layered-memory' },
        { text: 'Demo 3：BM25 + 向量 + RRF', link: '/demos/03-hybrid-search' },
        { text: 'Demo 4：接入一个 Agent Loop', link: '/demos/04-agent-loop' },
      ],
    },
    outline: { level: [2, 3] },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/TencentCloud/TencentDB-Agent-Memory' },
    ],
    footer: {
      message: '教学项目基于 TencentDB-Agent-Memory 的公开设计思想整理，示例代码为独立的简化实现。',
      copyright: 'MIT License',
    },
    search: { provider: 'local' },
  },
}))
