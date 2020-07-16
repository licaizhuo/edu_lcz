import Vue from 'vue'
import Vuex from 'vuex'
import da from "element-ui/src/locale/lang/da";

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        // 共享数据，购物车数量
        cart_length: 0
    },
    mutations: {
        // 检测提交购物车的动作
        get_cart_length(state, data) {
            state.cart_length = data;
            sessionStorage.cart_length = data
        }
    }
})
