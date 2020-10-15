import { RouteConfig } from 'vue-router'
import { AGENT_VIEW, AGENT_OPERATE } from '../action-map'
const AgentStatus = () => import(/* webpackChunkName: 'AgentStatus' */'@/views/agent/agent-list.vue')
const AgentSetup = () => import(/* webpackChunkName: 'AgentSetup' */'@/views/agent/agent-setup/agent-setup.vue')
const AgentImport = () => import(/* webpackChunkName: 'AgentImport' */'@/views/agent/agent-setup/agent-import.vue')
const AutoDiscovery = () => import(/* webpackChunkName: 'AutoDiscovery' */'@/views/discovery/auto-discovery.vue')

export default [
  {
    path: 'agent-manager/status',
    name: 'agentStatus',
    component: AgentStatus,
    meta: {
      navId: 'agentManager',
      title: 'Agent管理',
      authority: {
        page: AGENT_VIEW,
        operate: AGENT_OPERATE
      }
    }
  },
  {
    path: 'agent-manager/setup',
    name: 'agentSetup',
    component: AgentSetup,
    meta: {
      navId: 'agentManager',
      title: '普通安装',
      authority: {
        page: AGENT_OPERATE
      }
    }
  },
  {
    path: 'agent-manager/import',
    name: 'agentImport',
    props: true,
    component: AgentImport,
    meta: {
      navId: 'agentManager',
      title: 'Excel导入安装',
      authority: {
        page: AGENT_OPERATE
      }
    }
  },
  {
    path: 'agent-manager/edit',
    name: 'agentEdit',
    props: true,
    component: AgentImport,
    meta: {
      navId: 'agentManager',
      needBack: true,
      backConfirm: true,
      authority: {
        page: AGENT_OPERATE
      }
    }
  },
  {
    path: 'agent-manager/auto-discovery',
    name: 'autoDiscovery',
    component: AutoDiscovery,
    meta: {
      navId: 'agentManager',
      title: '自动发现'
    }
  }
] as RouteConfig[]
