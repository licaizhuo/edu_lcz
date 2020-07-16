<template>
    <div class="footer">
        <ul>
            <li v-for="(footer,index) in footer_list" :key="index">

                <a :href="footer.link" v-if="footer.is_site" style="color: #f0f0f0">{{footer.title}}</a>
                <router-link v-else :to="'/'+footer.link" style="color: #f0f0f0">{{footer.title}}</router-link>
            </li>
        </ul>
    </div>
</template>

<script>
    export default {
        name: "Footer", data() {
            return {
                footer_list: []
            }
        },
        methods: {
            get_all_banner() {
                this.$axios.get(this.$settings.HOST + "home/footer/").then(res => {
                    // console.log(res.data);
                    this.footer_list = res.data
                    // console.log(this.banner_list);
                    // for (let a in res.data) {
                    //     // console.log(a);
                    //     console.log(this.banner_list[a]);
                    // }
                }).catch(error => {

                })
            }
        },
        created() {
            this.get_all_banner()
        }
    }
</script>

<style scoped>
    .footer {
        width: 100%;
        height: 128px;
        background: #25292e;
        color: #fff;
    }

    .footer ul {
        margin: 0 auto 16px;
        padding-top: 38px;
        width: 810px;
    }

    .footer ul li {
        float: left;
        width: 112px;
        margin: 0 10px;
        text-align: center;
        font-size: 14px;
    }

    .footer ul::after {
        content: "";
        display: block;
        clear: both;
    }

    .footer p {
        text-align: center;
        font-size: 12px;
    }
</style>
