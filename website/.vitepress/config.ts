import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitepress'

type CatalogItem = {
  id: string
  order?: number
  displayOrder?: number
  unitLabel?: string
  title: string
  route: string
  outputs: Array<{ id: string; label: string; route: string }>
}

type CatalogEntry = {
  id: string
  title: string
  shortTitle?: string
  unitLabel?: string
  referenceRoute?: string
  practice?: Array<{ id: string }>
  items: CatalogItem[]
}

const generatedPath = fileURLToPath(new URL('./generated/catalog.json', import.meta.url))
const catalog = JSON.parse(readFileSync(generatedPath, 'utf8')) as CatalogEntry[]
const settingsPath = fileURLToPath(new URL('./generated/site.json', import.meta.url))
const settings = JSON.parse(readFileSync(settingsPath, 'utf8')) as {
  description: string
  site: { title: string; lang: string; base: string; repository: string }
  sections: Array<{ id: string; title: string }>
  referenceCollections: Array<{ title: string; route: string }>
}

function lectureSidebarItem(item: CatalogItem, unitLabel?: string) {
  return {
    text: `${item.order ? `${unitLabel ? `${unitLabel} ` : 'L'}${String(item.displayOrder ?? item.order).padStart(2, '0')} · ` : ''}${item.title}`,
    link: item.route,
  }
}

const courseSidebars = Object.fromEntries(catalog.map((course) => [
  `/generated/courses/${course.id}/`,
  [{
    text: course.shortTitle ?? course.title,
    link: `/generated/courses/${course.id}/`,
    items: [
      ...(course.referenceRoute ? [{ text: 'L00 · 课程参考资料', link: course.referenceRoute }] : []),
      ...(course.practice?.length ? [{ text: 'Lab 与作业', link: `/generated/courses/${course.id}/#lab-与作业` }] : []),
      ...course.items.map((item) => lectureSidebarItem(item, item.unitLabel ?? course.unitLabel)),
    ],
  }],
]))

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
      { text: '课程', link: '/', activeMatch: '^/$|^/generated/(courses|catalog)/' },
      { text: '资料库', link: '/generated/resources/', activeMatch: '^/generated/resources/|^/topics/|^/references/' },
      { text: '关于', link: '/about/', activeMatch: '^/about/|^/workflow/' },
    ],
    sidebar: {
      '/topics/': [
        {
          text: '配套阅读',
          items: settings.referenceCollections.map((collection) => ({ text: collection.title, link: collection.route })),
        },
      ],
      '/workflow/': [
        { text: '关于', link: '/about/' },
        { text: '维护文档', link: '/workflow/' },
      ],
      '/about/': [
        { text: '关于', link: '/about/' },
        { text: '维护文档', link: '/workflow/' },
      ],
      '/generated/resources/': [
        { text: '资料库', link: '/generated/resources/' },
        {
          text: '配套阅读',
          items: settings.referenceCollections.map((collection) => ({ text: collection.title, link: collection.route })),
        },
      ],
      '/references/': [
        { text: '课程网站参考', link: '/references/course-site-design' },
        { text: 'CS336 学习路径', link: '/generated/courses/cs336-2026/' },
        { text: '计算机科学资源地图', link: '/references/computer-science-resource-map' },
        { text: '维护文档', link: '/workflow/' },
      ],
      ...courseSidebars,
      '/generated/catalog/': [
        { text: '课程目录', link: '/generated/catalog/' },
        ...catalog.map((course) => ({ text: course.shortTitle ?? course.title, link: `/generated/courses/${course.id}/` })),
      ],
      '/': [
        {
          text: '课程分类',
          items: settings.sections.map((section) => ({ text: section.title, link: `/#${section.id}` })),
        },
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
