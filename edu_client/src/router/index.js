import Vue from 'vue'
import Router from 'vue-router'
import Home from "../components/Home";
import Login from "../components/Login";
import Register from "../components/Register";
import Course from "../components/Course";
import CourseDetail from "../components/CourseDetail";

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/home',
            name: 'home',
            component: Home
        },
        {
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/login',
            name: 'login',
            component: Login
        },
        {
            path: '/register',
            name: 'register',
            component: Register
        },
        {
            path: '/course',
            name: 'course',
            component: Course
        },
        {
            path: '/detail',
            name: 'detail',
            component: CourseDetail
        },
        {
            path: '/detail/:id',
            name: 'detail',
            component: CourseDetail
        },
    ]
})

