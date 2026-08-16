import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import CourseHero from './components/CourseHero.vue'
import CourseHeader from './components/CourseHeader.vue'
import HomeHero from './components/HomeHero.vue'
import LectureGrid from './components/LectureGrid.vue'
import CourseMap from './components/CourseMap.vue'
import CourseTabs from './components/CourseTabs.vue'
import PipelineFlow from './components/PipelineFlow.vue'
import SidebarToggle from './components/SidebarToggle.vue'
import LectureVideo from './components/LectureVideo.vue'
import LectureWorkspaceHero from './components/LectureWorkspaceHero.vue'
import LectureWorkspaceTabs from './components/LectureWorkspaceTabs.vue'
import LectureWorkspaceOutline from './components/LectureWorkspaceOutline.vue'
import CourseReferenceLibrary from './components/CourseReferenceLibrary.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'layout-top': () => h(SidebarToggle),
  }),
  enhanceApp({ app }) {
    app.component('CourseHero', CourseHero)
    app.component('CourseHeader', CourseHeader)
    app.component('HomeHero', HomeHero)
    app.component('LectureGrid', LectureGrid)
    app.component('CourseMap', CourseMap)
    app.component('CourseTabs', CourseTabs)
    app.component('PipelineFlow', PipelineFlow)
    app.component('LectureVideo', LectureVideo)
    app.component('LectureWorkspaceHero', LectureWorkspaceHero)
    app.component('LectureWorkspaceTabs', LectureWorkspaceTabs)
    app.component('LectureWorkspaceOutline', LectureWorkspaceOutline)
    app.component('CourseReferenceLibrary', CourseReferenceLibrary)
  },
}
