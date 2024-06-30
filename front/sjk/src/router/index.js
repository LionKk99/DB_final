import Vue from 'vue'
import VueRouter from 'vue-router'
import LogRes from '@/components/MyLogReg'
import user from '@/components/MyUser'
Vue.use(VueRouter)
export default new VueRouter({
    mode:'history',
    routes: [
        {
            path:'/',
            redirect:'/login'
        },
        {
            path: '/login',
            component: LogRes,
            meta: {
                title: "登录"
            },
        },
        {
            path: '/user',
            component: user,
            meta: {
                title: "用户界面"
            }
        },
    ]
})