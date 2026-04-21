import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Layout from '../layouts/MainLayout.vue'
import Home from '../views/Home.vue'
import PreEvaluation from '../views/PreEvaluation.vue'
import TenderList from '../views/TenderList.vue'
import TenderDetail from '../views/TenderDetail.vue'
import TenderInfoList from '../views/TenderInfoList.vue'
import TenderInfoDetail from '../views/TenderInfoDetail.vue'
import BidList from '../views/BidList.vue'
import ProposalEditor from '../views/ProposalEditor.vue'
import DemoWorkflow from '../views/DemoWorkflow.vue'
import PricingStrategy from '../views/PricingStrategy.vue'
import ProjectCreate from '../views/ProjectCreate.vue'
import Login from '../views/Login.vue'
import UserManagement from '../views/UserManagement.vue'
import RoleManagement from '../views/RoleManagement.vue'
import SystemSettings from '../views/SystemSettings.vue'
import { isLoggedIn } from '../services/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: Home
      },
      {
        path: 'pre-evaluation',
        name: 'PreEvaluation',
        component: PreEvaluation
      },
      {
        path: 'tender-list',
        name: 'TenderList',
        component: TenderList
      },
      {
        path: 'tender-info/:id',
        name: 'TenderInfoDetail',
        component: TenderInfoDetail
      },
      {
        path: 'tender-info-list',
        name: 'TenderInfoList',
        component: TenderInfoList
      },
      {
        path: 'tender-detail/:id',
        name: 'TenderDetail',
        component: TenderDetail
      },
      {
        path: 'bid-list',
        name: 'BidList',
        component: BidList
      },
      {
        path: 'bid-list/:projectId/tender-detail',
        name: 'TenderDetailProject',
        component: TenderDetail
      },
      {
        path: 'bid-list/:projectId/proposal',
        name: 'ProposalEditor',
        component: ProposalEditor
      },
      {
        path: 'proposal-editor',
        name: 'ProposalEditorOld',
        component: ProposalEditor
      },
      {
        path: 'demo-workflow',
        name: 'DemoWorkflow',
        component: DemoWorkflow
      },
      {
        path: 'pricing-strategy',
        name: 'PricingStrategy',
        component: PricingStrategy
      },
      {
        path: 'project-create',
        name: 'ProjectCreate',
        component: ProjectCreate
      },
      {
        path: 'user-management',
        name: 'UserManagement',
        component: UserManagement
      },
      {
        path: 'role-management',
        name: 'RoleManagement',
        component: RoleManagement
      },
      {
        path: 'system-settings',
        name: 'SystemSettings',
        component: SystemSettings
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  if (to.meta?.public) {
    next()
    return
  }
  if (!isLoggedIn()) {
    next('/login')
    return
  }
  next()
})

export default router
