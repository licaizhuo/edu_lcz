<template>
    <div class="login box">
        <img src="static/image/1111.jpg" alt="">
        <div class="login">
            <div class="login-title">
                <img src="../../static/image/logo.png" alt="">
                <p>百知教育给你最优质的学习体验!</p>
            </div>
            <div class="login_box">
                <div class="title">

                    <span @click="alter_select('1')" :id="select_pwd">密码登录</span>
                    <span @click="alter_select('2')" :id="select_msg">短信登录</span>
                </div>
                <div class="inp" v-if="is_select">
                    <input type="text" placeholder="用户名 / 手机号码" class="user" v-model="username">
                    <input type="password" name="" class="pwd" placeholder="密码" v-model="password">
                    <div id="geetest1"></div>
                    <div class="rember">
                        <p>
                            <el-checkbox v-model="remember_me">记住密码</el-checkbox>
                        </p>
                        <p>忘记密码</p>
                    </div>
                    <button class="login_btn btn btn-primary" @click="get_captcha">登录</button>
                    <p class="go_login">没有账号
                        <router-link to="/register">立即注册</router-link>
                    </p>
                </div>
                <div class="inp" v-else>
                    <input type="text" placeholder="手机号码" class="user" v-model="username">
                    <div class="sms-box">
                        <input v-model="password" type="text" maxlength="6" placeholder="输入验证码" class="user">
                        <div class="sms-btn" @click="get_code">{{sms_text}}</div>
                    </div>
                    <button class="login_btn btn btn-primary" @click="login_bz">登录</button>
                    <p class="go_login">没有账号
                        <router-link to="/register">立即注册</router-link>
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: "Login",
        data() {
            return {
                is_select: true,
                username: "",
                password: "",
                remember_me: false,
                is_sms: false,// 是否已经发送短信的状态
                sms_text: "点击发送验证码", //发送短信的提示
                select_pwd: "be_select",
                select_msg: "",
            }
        },
        methods: {
            login_bz() {
                this.$axios({
                    url: this.$settings.HOST + "user/login/",
                    method: "post",
                    data: {
                        username: this.username,
                        password: this.password,
                    },
                }).then(res => {
                    let token_time = new Date(new Date().getTime() + 60 * 60 * 1000);
                    this.$cookies.set("token", res.data.token, {
                        expires: token_time
                    });
                    this.$cookies.set("user_id", res.data.user_id);
                    let username = res.data.username
                    if (this.remember_me) {
                        let DAY = 30;
                        let password = this.$base64.Base64.encode(this.password)
                        let inFifteenMinutes = new Date(new Date().getTime() + DAY * 24 * 60 * 60 * 1000);
                        this.$cookies.set("username", username, {
                            expires: inFifteenMinutes
                        });
                        this.$cookies.set("password", password, {
                            expires: inFifteenMinutes
                        });
                    } else {
                        this.$cookies.set("username", username);
                        this.$cookies.remove("password");
                    }
                    this.$store.commit('get_cart_length', res.data.cart_length)
                    this.$message.success("登入成功，欢迎回来")
                    this.$router.go(-1)
                }).catch(error => {
                    this.$message.error("账号或密码出错，请您仔细检查哦~")
                })
            },
            handlerPopup(captchaObj) {
                let _this = this;
                captchaObj.onSuccess(function () {
                    var validate = captchaObj.getValidate();
                    _this.$axios({
                        url: _this.$settings.HOST + "user/captcha/",
                        method: "post",
                        data: {
                            username: _this.username,
                            geetest_challenge: validate.geetest_challenge,
                            geetest_validate: validate.geetest_validate,
                            geetest_seccode: validate.geetest_seccode
                        },
                    }).then(res => {
                        // console.log(res.data.status)
                        if (res.data && (res.data.status === "success")) {
                            _this.login_bz()
                        }

                    }).catch(error => {
                        _this.$message.error("出现错误，请刷新页面，重新登入。")
                    })
                });
                document.getElementById('geetest1').innerHTML = ""
                captchaObj.appendTo("#geetest1")
            },
            get_captcha() {
                this.$axios({
                    url: this.$settings.HOST + "user/captcha/",
                    method: "get",
                    params: {
                        username: this.username
                    }
                }).then(res => {
                    let data = JSON.parse(res.data);
                    // console.log(data);
                    initGeetest({
                        gt: data.gt,
                        challenge: data.challenge,
                        product: "popup", // 产品形式，包括：float，embed，popup。注意只对PC版验证码有效
                        offline: !data.success, // 表示用户后台检测极验服务器是否宕机，一般不需要关注
                        new_captcha: data.new_captcha
                    }, this.handlerPopup);
                }).catch(error => {
                    this.$message.error("账号或密码出错，请您仔细检查哦~")
                })

            },
            get_code() {
                if (this.is_sms) {
                    return false
                }
                if ((/^1[3456789]\d{9}$/.test(this.username))) {
                    this.$axios({
                        url: this.$settings.HOST + "user/sms/?select=2&mobile=" + `${this.username}`,
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
            },
            alter_select(select_flag) {
                if (select_flag === '1') {
                    this.is_select = true
                    this.select_msg = ""
                    this.select_pwd = "be_select"
                    this.password = ""
                    this.username = ""
                } else {
                    this.is_select = false
                    this.select_pwd = ""
                    this.select_msg = "be_select"
                    this.password = ""
                    this.username = ""
                }
            }
        },
        created() {
            if (this.$cookies.get('token')) {
                this.$router.push('/')
            }
            let username = this.$cookies.get("username");
            let password = this.$cookies.get("password");
            if (username && password) {
                this.username = username
                this.password = this.$base64.Base64.decode(password)
                this.remember_me = true
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

    .sms-box {
        position: relative;
    }

    .box .login {
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

    .login .login-title {
        width: 100%;
        text-align: center;
    }

    .login-title img {
        width: 190px;
        height: auto;
    }

    .login-title p {
        font-family: PingFangSC-Regular;
        font-size: 18px;
        color: #fff;
        letter-spacing: .29px;
        padding-top: 10px;
        padding-bottom: 50px;
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

    .login_box {
        width: 400px;
        height: auto;
        background: #fff;
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .5);
        border-radius: 4px;
        margin: 0 auto;
        padding-bottom: 40px;
    }

    .login_box .title {
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

    .login_box #be_select {
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

    .login_btn {
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


</style>
