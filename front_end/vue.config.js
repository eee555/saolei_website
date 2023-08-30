module.exports = {
    publicPath: './',
    assetsDir: 'static',


    devServer: {
        open: true,
        proxy: {
            '/userprofile': {
                target: 'http://127.0.0.1:8000/',//要代理的本地api地址，也可以换成线上测试地址
                changeOrigin: true,//允许跨域
                pathRewrite:{"^/userprofile":"/userprofile"}//将/api开头替换为/api
            }
        }
    },
    lintOnSave: false// 屏蔽EsLint
}