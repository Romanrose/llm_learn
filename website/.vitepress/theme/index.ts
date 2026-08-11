import DefaultTheme from 'vitepress/theme'
import CourseHeader from './components/CourseHeader.vue'
import LectureGrid from './components/LectureGrid.vue'
import CourseMap from './components/CourseMap.vue'
import CourseTabs from './components/CourseTabs.vue'
import PipelineFlow from './components/PipelineFlow.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('CourseHeader', CourseHeader)
    app.component('LectureGrid', LectureGrid)
    app.component('CourseMap', CourseMap)
    app.component('CourseTabs', CourseTabs)
    app.component('PipelineFlow', PipelineFlow)
  },
}
