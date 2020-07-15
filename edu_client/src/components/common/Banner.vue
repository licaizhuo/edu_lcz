<template>
    <el-carousel height="720px" :interval="3000" arrow="always">
        <el-carousel-item v-for="(banner,index) in banner_list" :key="index">
            <a :href="banner.link"><img :src="banner.img" :alt="banner.title"></a>
        </el-carousel-item>
    </el-carousel>
</template>

<script>
    export default {
        name: "Banner",
        data() {
            return {
                banner_list: []
            }
        },
        methods: {
            get_all_banner() {
                this.$axios.get(this.$settings.HOST + "home/banner/").then(res => {
                    // console.log(res.data);
                    this.banner_list = res.data
                    // console.log(this.banner_list instanceof Array);
                    // console.log(this.banner_list);
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
    .el-carousel__item h3 {
        color: #475669;
        font-size: 18px;
        opacity: 0.75;
        line-height: 300px;
        margin: 0;
    }

    .el-carousel__item:nth-child(2n) {
        background-color: #99a9bf;
    }

    .el-carousel__item:nth-child(2n+1) {
        background-color: #d3dce6;
    }
</style>
