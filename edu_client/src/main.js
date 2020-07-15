// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import axios from 'axios'
import cookies from 'js-cookie'
import base64 from 'js-base64'

Vue.prototype.$axios = axios
Vue.prototype.$cookies = cookies
Vue.prototype.$base64 = base64
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import '../static/js/gt'

require('video.js/dist/video-js.css');
require('vue-video-player/src/custom-theme.css');
import VideoPlayer from 'vue-video-player'

Vue.use(VideoPlayer);


Vue.use(ElementUI)
import settings from "./settings";
import "../static/css/global.css"
import th from "element-ui/src/locale/lang/th";

Vue.prototype.$settings = settings
Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    components: {App},
    template: '<App/>'
})
