import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitepress'

type CatalogItem = {
  id: string
  order?: number
  title: string
  route: string
  outputs: Array<{ id: string; label: string; route: string }>
}

type CatalogEntry = {
  id: string
  title: string
  shortTitle?: string
  items: CatalogItem[]
}

const generatedPath = fileURLToPath(new URL('./generated/catalog.json', import.meta.url))
const catalog = JSON.parse(readFileSync(generatedPath, 'utf8')) as CatalogEntry[]
const settingsPath = fileURLToPath(new URL('./generated/site.json', import.meta.url))
const settings = JSON.parse(readFileSync(settingsPath, 'utf8')) as {
  description: string
  site: { title: string; lang: string; base: string; repository: string }
}

const courseSidebar = catalog.flatMap((course) => [
  {
    text: course.shortTitle ?? course.title,
    link: `/generated/courses/${course.id}/`,
    items: course.items.map((item) => ({
      text: `${item.order ? `Lecture ${item.order} · ` : ''}${item.title}`,
      link: item.route,
      ...(item.outputs.length
        ? {
            collapsed: true,
            items: item.outputs.map((output) => ({ text: output.label, link: output.route })),
          }
        : {}),
    })),
  },
])

export default defineConfig({
  lang: settings.site.lang,
  title: settings.site.title,
  description: settings.description,
  base: settings.site.base,
  cleanUrls: true,
  ignoreDeadLinks: [/^\/generated\/exports\/.*\.tex$/],
  lastUpdated: true,
  sitemap: { hostname: 'https://romanrose.github.io/llm_learn/' },
  head: [
    ['meta', { name: 'theme-color', content: '#0d766e' }],
    ['meta', { property: 'og:site_name', content: 'llm_learn' }],
  ],
  markdown: {
    math: true,
    image: { lazyLoading: true },
    lineNumbers: true,
  },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '课程', link: '/#course-map' },
      { text: 'CS336', link: '/generated/courses/cs336-2026/' },
      { text: 'Course 工作流', link: '/workflow/' },
      { text: '关于', link: '/about' },
    ],
    sidebar: {
      '/topics/': [
        {
          text: '专题地图',
          items: [
            { text: '智能体与 Agent', link: '/topics/agent/' },
            { text: 'AI Infra 与工程', link: '/topics/infra/' },
            { text: '论文与技术文章', link: '/topics/papers/' },
            { text: '演讲、访谈与延伸阅读', link: '/topics/interviews/' },
          ],
        },
      ],
      '/workflow/': [
        { text: 'Course 工作流', link: '/workflow/' },
        { text: '关于 llm_learn', link: '/about' },
      ],
      '/generated/courses/': courseSidebar,
      '/generated/catalog/': [
        { text: '知识地图', link: '/generated/catalog/' },
        ...catalog.map((course) => ({ text: course.shortTitle ?? course.title, link: `/generated/courses/${course.id}/` })),
      ],
      '/': [
        { text: '首页', link: '/' },
        {
          text: '课程地图',
          items: [
            { text: '大模型课程', link: '/#llm-courses' },
            { text: '智能体与 Agent', link: '/#agent' },
            { text: 'AI Infra 与工程', link: '/#infra' },
            { text: '论文与技术文章', link: '/#papers' },
            { text: '演讲、访谈与延伸阅读', link: '/#interviews' },
          ],
        },
        {
          text: '专题',
          items: [
            { text: 'Agent', link: '/topics/agent/' },
            { text: 'Infra', link: '/topics/infra/' },
            { text: 'Papers', link: '/topics/papers/' },
            { text: 'Interviews', link: '/topics/interviews/' },
          ],
        },
        { text: 'Course 工作流', link: '/workflow/' },
      ],
    },
    outline: { level: [2, 3], label: '本页内容' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    lastUpdated: { text: '最后更新' },
    darkModeSwitchLabel: '外观',
    sidebarMenuLabel: '目录',
    returnToTopLabel: '回到顶部',
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: { buttonText: '搜索', buttonAriaLabel: '搜索' },
              modal: {
                noResultsText: '没有找到相关内容',
                resetButtonTitle: '清除查询',
                footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' },
              },
            },
          },
        },
      },
    },
    socialLinks: [{ icon: 'github', link: settings.site.repository }],
    footer: {
      message: '资料来源归原作者与课程方所有 · 笔记内容持续校订',
      copyright: 'llm_learn',
    },
  },
})
