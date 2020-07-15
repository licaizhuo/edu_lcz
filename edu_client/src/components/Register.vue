<template>
    <div class="box">
        <img src="../../static/image/1111.jpg" alt="">
        <div class="register">
            <div class="register_box">
                <div class="register-title">百知教育在线平台注册</div>
                <div class="inp">
                    <input v-model="phone" type="text" placeholder="手机号码" class="user" @blur="check_phone">
                    <input v-model="password" type="password" placeholder="登录密码" class="user">
                    <div id="geetest"></div>
                    <div class="sms-box">
                        <input v-model="code" type="text" maxlength="6" placeholder="输入验证码" class="user">
                        <div class="sms-btn" @click="get_code">{{sms_text}}</div>
                    </div>
                    <button class="register_btn" @click="user_register" id="register_new_user">注册</button>
                    <p class="go_login">已有账号
                        <router-link to="/login">直接登录</router-link>
                        <!--                        <span>直接登录</span>-->
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: "Register",
        data() {
            return {
                phone: "",
                password: "",
                code: "",
                phone_is_qualified: false,
                is_sms: false,// 是否已经发送短信的状态
                sms_text: "点击发送验证码", //发送短信的提示
            }
        },
        methods: {
            user_register() {
                if (this.phone_is_qualified) {
                    this.$axios({
                        url: this.$settings.HOST + "user/register/",
                        method: "post",
                        data: {
                            "phone": this.phone,
                            "password": this.password,
                            'sms_code': this.code
                        },
                    }).then(res => {
                        this.$message.success("注册成功，正在进行登入")
                        let token_time = new Date(new Date().getTime() + 20 * 60 * 1000);
                        this.$cookies.set("token", res.data.token, {
                            expires: token_time
                        });
                        this.$cookies.set("user_id", res.data.user_id);
                        let username =
                            this.$cookies.set("username", res.data.username);
                        this.$message.success("登入成功")
                        this.$router.push('/')
                    }).catch(error => {
                        this.$message.error(error.response.data.non_field_errors[0])
                        // console.log(error.response.data.non_field_errors[0])
                    })
                } else {
                    this.$message.error("手机号不合格")
                }

            },
            check_phone() {

                if ((/^1[3456789]\d{9}$/.test(this.phone))) {
                    this.$axios({
                        url: this.$settings.HOST + "user/check_phone/?phone=" + `${this.phone}`,
                        method: "get",
                    }).then(res => {
                        this.phone_is_qualified = true
                    }).catch(error => {
                        this.$message.error(error.response.data[0])

                        this.phone_is_qualified = false
                    })
                } else {
                    this.$message.error("手机号不符合规范")
                }

            },
            get_code() {
                if (this.is_sms) {
                    return false
                }
                if ((/^1[3456789]\d{9}$/.test(this.phone))) {
                    this.$axios({
                        url: this.$settings.HOST + "user/sms/?select=1&mobile=" + `${this.phone}`,
                        method: "get"
                    }).then(res => {
                        this.$message.success("发送成功,请等待并注意查收")
                    }).catch(error => {
                        this.$message.error(error.response.data[0])
                    })
                    this.is_sms = true
                    let interval = 60
                    let timer = setInterval(() => {
                        if (interval <= 1) {
                            clearInterval(timer)
                            this.is_sms = false
                            this.sms_text = "点击发送验证码"
                        } else {
                            interval--
                            this.sms_text = `${interval}点击发送验证码`
                        }
                    }, 1000)
                } else {
                    this.$message.error("手机号不符合规范")
                }
            }
        }
    }
</script>

<style scoped>
    .box {
        width: 100%;
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .box img {
        width: 100%;
        min-height: 100%;
    }

    .box .register {
        position: absolute;
        width: 500px;
        height: 400px;
        top: 0;
        left: 0;
        margin: auto;
        right: 0;
        bottom: 0;
        top: -338px;
    }

    .register .register-title {
        width: 100%;
        font-size: 24px;
        text-align: center;
        padding-top: 30px;
        padding-bottom: 30px;
        color: #4a4a4a;
        letter-spacing: .39px;
    }

    .register-title img {
        width: 190px;
        height: auto;
    }

    .register-title p {
        font-family: PingFangSC-Regular;
        font-size: 18px;
        color: #fff;
        letter-spacing: .29px;
        padding-top: 10px;
        padding-bottom: 50px;
    }

    .register_box {
        width: 400px;
        height: auto;
        background: #fff;
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .5);
        border-radius: 4px;
        margin: 0 auto;
        padding-bottom: 40px;
    }

    .register_box .title {
        font-size: 20px;
        color: #9b9b9b;
        letter-spacing: .32px;
        border-bottom: 1px solid #e6e6e6;
        display: flex;
        justify-content: space-around;
        padding: 50px 60px 0 60px;
        margin-bottom: 20px;
        cursor: pointer;
    }

    .register_box .title span:nth-of-type(1) {
        color: #4a4a4a;
        border-bottom: 2px solid #84cc39;
    }

    .inp {
        width: 350px;
        margin: 0 auto;
    }

    .inp input {
        border: 0;
        outline: 0;
        width: 100%;
        height: 45px;
        border-radius: 4px;
        border: 1px solid #d9d9d9;
        text-indent: 20px;
        font-size: 14px;
        background: #fff !important;
    }

    .inp input.user {
        margin-bottom: 16px;
    }

    .inp .rember {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        margin-top: 10px;
    }

    .inp .rember p:first-of-type {
        font-size: 12px;
        color: #4a4a4a;
        letter-spacing: .19px;
        margin-left: 22px;
        display: -ms-flexbox;
        display: flex;
        -ms-flex-align: center;
        align-items: center;
        /*position: relative;*/
    }

    .inp .rember p:nth-of-type(2) {
        font-size: 14px;
        color: #9b9b9b;
        letter-spacing: .19px;
        cursor: pointer;
    }

    .inp .rember input {
        outline: 0;
        width: 30px;
        height: 45px;
        border-radius: 4px;
        border: 1px solid #d9d9d9;
        text-indent: 20px;
        font-size: 14px;
        background: #fff !important;
    }

    .inp .rember p span {
        display: inline-block;
        font-size: 12px;
        width: 100px;
        /*position: absolute;*/
        /*left: 20px;*/

    }

    #geetest {
        margin-top: 20px;
    }

    .register_btn {
        width: 100%;
        height: 45px;
        background: #84cc39;
        border-radius: 5px;
        font-size: 16px;
        color: #fff;
        letter-spacing: .26px;
        margin-top: 30px;
    }

    .inp .go_login {
        text-align: center;
        font-size: 14px;
        color: #9b9b9b;
        letter-spacing: .26px;
        padding-top: 20px;
    }

    .inp .go_login span {
        color: #84cc39;
        cursor: pointer;
    }

    .sms-box {
        position: relative;
    }

    .sms-btn {
        font-size: 14px;
        color: #ffc210;
        letter-spacing: .26px;
        position: absolute;
        right: 16px;
        top: 10px;
        cursor: pointer;
        overflow: hidden;
        background: #fff;
        border-left: 1px solid #484848;
        padding-left: 16px;
        padding-bottom: 4px;
    }
</style>
