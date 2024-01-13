import axios from 'axios'
// import { AXIOS_BASE_URL } from './config';

axios.defaults.headers['Content-Type'] = 'application/x-www-form-urlencoded';
axios.defaults.baseURL = process.env.VUE_APP_BASE_API;
const $axios = axios.create({
    timeout: 2000,
    withCredentials: true   // 必须指定这个参数，否则axios才能携带参数
})
// declare module 'axios' {
//     interface AxiosInstance {
//         (config: AxiosRequestConfig): Promise<any>
//     }
// }


export default $axios






// import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
// import { ElLoading } from 'element-plus';


// let loading: any;

// const startLoading = () => {

//   interface Options {
//     lock: boolean;
//     text: string;
//     background: string;
//   };

//   const options: Options = {
//     lock: true,
//     text: "加载中...",
//     background: 'rgba(0,0,0,0.7)'
//   }
//   loading = ElLoading.service(options);
// }

// const endLoading = () => {
//   loading.close();
// }

// // 请求拦截
// axios.interceptors.request.use((config: AxiosRequestConfig) => {
//   // 加载
//   startLoading();
//   return config;
// })


// // 响应拦截
// axios.interceptors.response.use((response: AxiosResponse<any>) => {
//   // 结束loading
//   endLoading();
//   return response;
// }, error => {
//   // 结束loading
//   endLoading();
//   // 错误提醒
//   return Promise.reject(error);
// })

// export default axios;