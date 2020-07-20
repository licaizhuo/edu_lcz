<template>
    <div class="cart_item" id="cart_item_delete">
        <div class="cart_column column_1">
            <el-checkbox class="my_el_checkbox" v-model="course.selected"></el-checkbox>
        </div>
        <div class="cart_column column_2">
            <router-link :to="'/detail/'+course.id">
                <img :src="course.course_img" alt="">
                <span>{{course.name}}</span>
            </router-link>
        </div>
        <div class="cart_column column_3">
            <el-select v-model="course.expire_id" size="mini" placeholder="请选择购买有效期" class="my_el_select">
                <el-option v-for="item in course.expire_list" :label="item.expire_text" :value="item.id"
                           :key="item.id"></el-option>
            </el-select>
        </div>
        <div class="cart_column column_4">¥{{course.course_real_price}}</div>

        <div class="cart_column column_4">
            <el-link type="danger" @click="del_cart_course">删除</el-link>
        </div>
    </div>
</template>

<script>
    export default {
        name: "CartItem",
        //接收父组件传递的参数
        props: ['course'],
        watch: {
            'course.selected': function () {
                this.change_select()
            },
            'course.expire_id': function () {
                this.change_expire()
            },
        },
        data() {
            return {}
        },
        methods: {
            check_token() {
                let token = this.$cookies.get('token')
                if (!token) {
                    let self = this
                    this.$alert('对不起！登陆过期，请重新登入', {
                        callback() {
                            self.$router.push(('/login'))
                        }
                    });
                } else {
                    return token
                }
            },
            change_select() {
                let token = this.check_token()
                this.$axios.patch(`${this.$settings.HOST}cart/option/`, {
                        selected: this.course.selected,
                        course_id: this.course.id
                    },
                    {
                        headers: {
                            "Authorization": "jwt " + token
                        }
                    }).then(res => {
                    this.$message.success(res.data.message)
                    this.$emit('change_success')
                }).catch(error => {
                    this.$message.error("出现未知错误，请刷新页面")
                })
            },
            change_expire() {
                let token = this.check_token()
                this.$axios({
                    url: `${this.$settings.HOST}cart/option/`,
                    method: 'put',
                    headers: {
                        "Authorization": "jwt " + token
                    },
                    data: {
                        course_id: this.course.id,
                        expire_id: this.course.expire_id,
                    },
                }).then(res => {
                    this.$message.success(res.data.message)
                    this.course.course_real_price = res.data.course_real_price
                    this.$emit('change_success')
                }).catch(error => {
                    this.$message.error(error.response.data.message)
                })
            },
            del_cart_course() {
                let token = this.check_token()
                this.$confirm('将删除该用户, 是否确定?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios({
                        url: `${this.$settings.HOST}cart/option/`,
                        method: 'delete',
                        headers: {
                            "Authorization": "jwt " + token
                        },
                        data: {
                            course_id: this.course.id,
                        },
                    }).then(res => {
                        this.$message.success(res.data.message)
                        this.$store.commit('get_cart_length', res.data.cart_length)
                        this.$emit('delete_success')
                    }).catch(error => {
                        this.$message.error(error.response.data.message)
                    })
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });
            },
        },
    }
</script>

<style scoped>
    .cart_item::after {
        content: "";
        display: block;
        clear: both;
    }

    .cart_column {
        float: left;
        height: 250px;
    }

    .cart_item .column_1 {
        width: 88px;
        position: relative;
    }

    .my_el_checkbox {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        top: 0;
        margin: auto;
        width: 16px;
        height: 16px;
    }

    .cart_item .column_2 {
        padding: 67px 10px;
        width: 520px;
        height: 116px;
    }

    .cart_item .column_2 img {
        width: 175px;
        height: 115px;
        margin-right: 35px;
        vertical-align: middle;
    }

    .cart_item .column_3 {
        width: 197px;
        position: relative;
        padding-left: 10px;
    }

    .my_el_select {
        width: 117px;
        height: 28px;
        position: absolute;
        top: 0;
        bottom: 0;
        margin: auto;
    }

    .cart_item .column_4 {
        padding: 67px 10px;
        height: 116px;
        width: 142px;
        line-height: 116px;
    }

</style>

