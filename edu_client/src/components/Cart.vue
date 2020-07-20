<template>
    <div class="cart">
        <Header></Header>
        <div class="cart_info">
            <div class="cart_title">
                <span class="text">我的购物车</span>
                <span class="total">共{{this.$store.state.cart_length}}门课程</span>
            </div>
            <div class="cart_table">
                <div class="cart_head_row">
                    <span class="doing_row"></span>
                    <span class="course_row">课程</span>
                    <span class="expire_row">有效期</span>
                    <span class="price_row">单价</span>
                    <span class="do_more">操作</span>
                </div>
                <div class="cart_course_list">
                    <!--                    <div v-for="(course,index) in cart_list" :key="index">-->
                    <!--                        <CartItem :course="course" :index="index" @delete_success="delete_success"></CartItem>-->
                    <!--                    </div>-->
                    <CartItem v-for="(course,index) in cart_list" :key="index" :course="course" :index="index"
                              @delete_success="delete_success(index)" @change_success="cart_total_price"></CartItem>
                </div>
                <div class="cart_footer_row">
                    <span class="cart_select" style="display: inline-block; width: 70px;">
                        <el-link type="warning">
                        <label @click="if_select_all">
                            <el-checkbox v-model="select_all" v-if="select_all">全不选</el-checkbox>
                            <el-checkbox v-model="select_all" v-else>全选</el-checkbox>
                        </label>
                        </el-link>
                    </span>
                    <span class="cart_delete">
                        <el-link type="danger" @click="delete_select">
                        <i class="el-icon-delete" style="font-size: 15px;line-height: 19px">删除所选</i>
                        </el-link>
                    </span>
                    <router-link to="/order"><span class="goto_pay">去结算</span></router-link>
                    <span class="cart_total">总计：¥{{total_price}}</span>
                </div>
            </div>
        </div>
        <Footer></Footer>
    </div>
</template>

<script>
    import CartItem from "./common/CartItem";
    import Header from "./common/Header";
    import Footer from "./common/Footer";

    export default {
        name: "Cart",
        data() {
            return {
                cart_list: [],
                select_all: false,
                total_price: 0.00,
            }
        },
        methods: {
            delete_success(index) {
                this.cart_list.splice(index)
                this.cart_total_price()
            },
            cart_total_price() {
                let total_price = 0
                this.cart_list.forEach((course, key) => {
                    if (course.selected) {
                        total_price += parseFloat(course.course_real_price)
                    }
                })
                this.total_price = total_price
            },
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
            if_select_all() {
                let token = this.check_token()
                this.$axios.put(`${this.$settings.HOST}cart/option_all/`, {
                    "select_all": !this.select_all
                }, {
                    headers: {
                        "Authorization": "jwt " + token
                    }
                }).then(res => {
                    for (let index in this.cart_list) {
                        this.cart_list[index].selected = this.select_all
                    }
                    this.cart_total_price()
                }).catch(error => {
                    this.$message.error("出现未知错误，请刷新页面")
                })
            },
            delete_select() {
                let token = this.check_token()
                this.$confirm('将删除该用户, 是否确定?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios.delete(`${this.$settings.HOST}cart/option_all/`, {
                        headers: {
                            "Authorization": "jwt " + token
                        }
                    }).then(res => {
                        let len = this.cart_list.length
                        let flag_len = 0
                        for (let index = 0; index < len; index++) {
                            flag_len++
                            if (this.cart_list[index].selected) {
                                this.cart_list.splice(index, 1)
                                index--
                            }
                            if (flag_len === len) {
                                break
                            }
                        }
                        this.$store.commit('get_cart_length',this.cart_list.length)
                        this.cart_total_price()
                    }).catch(error => {
                        this.$message.error("出现未知错误，请刷新页面")
                    })
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });

            },
            get_cart(token) {
                if (!token) {
                    return false
                }
                this.$axios.get(`${this.$settings.HOST}cart/option/`, {
                    headers: {
                        "Authorization": "jwt " + token
                    }
                }).then(res => {
                    // console.log(res.data)
                    this.cart_list = res.data
                    this.$store.commit('get_cart_length', res.data.length)
                    this.cart_total_price()
                }).catch(error => {
                    this.$message.error("出现未知错误，请刷新页面")
                })
            }
        },
        components: {
            CartItem, Header, Footer
        },
        created() {
            let token = this.check_token()
            if (token) {
                this.get_cart(token)
            }
        }
    }
</script>

<style scoped>
    .cart_info {
        width: 1200px;
        margin: 0 auto 200px;
    }

    .cart_title {
        margin: 25px 0;
    }

    .cart_title .text {
        font-size: 18px;
        color: #666;
    }

    .cart_title .total {
        font-size: 12px;
        color: #d0d0d0;
    }

    .cart_table {
        width: 1170px;
    }

    .cart_table .cart_head_row {
        background: #F7F7F7;
        width: 100%;
        height: 80px;
        line-height: 80px;
        padding-right: 30px;
    }

    .cart_table .cart_head_row::after {
        content: "";
        display: block;
        clear: both;
    }

    .cart_table .cart_head_row .doing_row,
    .cart_table .cart_head_row .course_row,
    .cart_table .cart_head_row .expire_row,
    .cart_table .cart_head_row .price_row,
    .cart_table .cart_head_row .do_more {
        padding-left: 10px;
        height: 80px;
        float: left;
    }

    .cart_table .cart_head_row .doing_row {
        width: 78px;
    }

    .cart_table .cart_head_row .course_row {
        width: 530px;
    }

    .cart_table .cart_head_row .expire_row {
        width: 188px;
    }

    .cart_table .cart_head_row .price_row {
        width: 162px;
    }

    .cart_table .cart_head_row .do_more {
        width: 162px;
    }

    .cart_footer_row {
        padding-left: 30px;
        background: #F7F7F7;
        width: 100%;
        height: 80px;
        line-height: 80px;
    }

    .cart_footer_row .cart_select span {
        margin-left: -7px;
        font-size: 18px;
        color: #666;
    }

    .cart_footer_row .cart_delete {
        margin-left: 58px;
    }

    .cart_delete .el-icon-delete {
        font-size: 18px;
    }

    .cart_delete span {
        margin-left: 15px;
        cursor: pointer;
        font-size: 18px;
        color: #666;
    }

    .cart_total {
        float: right;
        margin-right: 62px;
        font-size: 18px;
        color: #666;
    }

    .goto_pay {
        float: right;
        width: 159px;
        height: 80px;
        outline: none;
        border: none;
        background: #ffc210;
        font-size: 18px;
        color: #fff;
        text-align: center;
        cursor: pointer;
    }
</style>
