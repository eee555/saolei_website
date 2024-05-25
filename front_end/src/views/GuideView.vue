<template>
    <el-row class="tac">
        <el-col :span="4">
            <h5 class="mb-2">目录</h5>
            <el-menu @select="show_content" class="el-menu-vertical">
                <el-sub-menu index="1">
                    <template #title>
                        <el-icon>
                            <Document />
                        </el-icon>
                        <span>公告</span>
                    </template>
                    <template v-for="(item, idx) in notice_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`1-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                <el-sub-menu v-else :index="`1-${idx + 1}`">
                                    <template #title>{{ item.name }}</template>
                                    <template v-for="(i, idy) in item.files">
                                        <el-menu-item :index="`1-${idx + 1}-${idy + 1}`">
                                            {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                    </template>
                                </el-sub-menu>
                    </template>
                </el-sub-menu>
                <el-sub-menu index="2">
                    <template #title>
                        <el-icon>
                            <Guide />
                        </el-icon>
                        <span>教程</span>
                    </template>
                    <template v-for="(item, idx) in guide_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`2-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                <el-sub-menu v-else :index="`2-${idx + 1}`">
                                    <template #title>{{ item.name }}</template>
                                    <template v-for="(i, idy) in item.files">
                                        <el-menu-item :index="`2-${idx + 1}-${idy + 1}`">
                                            {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                    </template>
                                </el-sub-menu>
                    </template>
                </el-sub-menu>
                <el-sub-menu index="3">
                    <template #title>
                        <el-icon>
                            <Cpu />
                        </el-icon>
                        <span>技术</span>
                    </template>
                    <template v-for="(item, idx) in tech_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`3-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                <el-sub-menu v-else :index="`3-${idx + 1}`">
                                    <template #title>{{ item.name }}</template>
                                    <template v-for="(i, idy) in item.files">
                                        <el-menu-item :index="`3-${idx + 1}-${idy + 1}`">
                                            {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                    </template>
                                </el-sub-menu>
                    </template>
                </el-sub-menu>
                <el-sub-menu index="4">
                    <template #title>
                        <el-icon>
                            <Grid />
                        </el-icon>
                        <span>其他</span>
                    </template>
                    <template v-for="(item, idx) in other_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`4-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                <el-sub-menu v-else :index="`4-${idx + 1}`">
                                    <template #title>{{ item.name }}</template>
                                    <template v-for="(i, idy) in item.files">
                                        <el-menu-item :index="`4-${idx + 1}-${idy + 1}`">
                                            {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }} </el-menu-item>
                                    </template>
                                </el-sub-menu>
                    </template>
                </el-sub-menu>
            </el-menu>
        </el-col>


        <el-col :span="20">
            <div style="padding-top: 20px;padding-left: 60px;" v-html="article_html" />
        </el-col>
    </el-row>
</template>

<script lang="ts" setup>
import { onMounted, ref, computed } from 'vue';
import useCurrentInstance from "@/utils/common/useCurrentInstance";
const { proxy } = useCurrentInstance();


// https://mdit-plugins.github.io/zh/
import MarkdownIt from 'markdown-it';
// 缩写悬停弹气泡
import { abbr } from "@mdit/plugin-abbr";
// 对齐方式
import { align } from "@mdit/plugin-align";
// 代码高亮
import markdownItHighlight from 'markdown-it-highlightjs';
// 数学公式
import mathjax3 from "markdown-it-mathjax3";
// 图片懒加载
import { imgLazyload } from "@mdit/plugin-img-lazyload";

const markdown = new MarkdownIt({
    html: true, // 允许HTML语法
    typographer: true, // 启用Typographer插件，可以更好地处理中文字符和标点符号
    linkify: true // 自动将文本中的URL转换为链接
}).use(abbr).use(align).use(markdownItHighlight).use(mathjax3).use(imgLazyload);

const js = `
2. 气泡：  

*[3BV]: Bechtel's Board Benchmark Value，可进一步简称BV。3BV指仅使用左键解开当前局面，所需要的理论最少左击次数。
*[STNB]: 计算公式初级为47.299/（Time^1.7/Solved 3BV）；中级为153.73/（Time^1.7/Solved 3BV）；高级为435.001/（Time^1.7/Solved 3BV），越大越好。
3BV 和 STNB 都是常用的术语，鼠标悬停在上面可以看到它们的解释。

3. 引用：  
> 这是单行引用

> 这是块状引用  
这是第二行  
这是第三行

- [x] dfgfdgd
- [ ] rgthrthrth
- [x] dfgfdgd
- [ ] rgthrthrth
- [x] dfgfdgd
- [ ] rgthrthrth

Here is a footnote reference,[^1] and another.[^longnote]

[^1]: Here is the footnote.

[^longnote]: Here's one with multiple blocks.


上标：$a^4$

$\\sqrt{3x-1}+(1+x)^2$

$$
\\left|\\begin{matrix}
    a & b & c \\\\
    d & e & f \\\\
    g & h & i
   \\end{matrix} \\right|
 $$

 # markdown-it rulezz!
 

`
// console.log(js);

const content = ref<string>("");

const article_html = computed(() => {
    return markdown.render(content.value);
})

// 子类别
type child_list = {
    // 子类别的排序依据
    index: number,
    name: string,
    // 子类别的文件名列表
    files: string[]
}
const notice_list = ref<child_list[]>([])
const guide_list = ref<child_list[]>([])
const tech_list = ref<child_list[]>([])
const other_list = ref<child_list[]>([])


onMounted(() => {
    // content.value = js;return
    proxy.$axios.get('/article/articles/'
    ).then(function (response) {
        const articles: string[] = response.data;
        for (const article of articles) {
            // 后端保证文章标题必须是此种格式，例如："[60.公告]明天下雨.md"
            const labels = article.match(/(?<=\[).*(?=\])/)![0].split(".");
            const index_i = /^[0-9]+$/.test(labels[0]) ? +labels[0] : 999;
            const child_name_i = ["公告", "教程", "技术", "其他"].includes(labels.at(-1)!) ? article : labels.at(-1)!;
            if (labels.includes("公告")) {
                const child_name_idx = notice_list.value.findIndex((v) => {
                    return v.name == child_name_i
                })
                if (child_name_idx >= 0) {
                    notice_list.value[child_name_idx].files.push(article);
                    notice_list.value[child_name_idx].index =
                        Math.min(notice_list.value[child_name_idx].index, index_i);
                } else {
                    notice_list.value.push({
                        index: index_i,
                        name: child_name_i,
                        files: [article],
                    })
                }
            } else if (labels.includes("教程")) {
                const child_name_idx = guide_list.value.findIndex((v) => {
                    return v.name == child_name_i
                })
                if (child_name_idx >= 0) {
                    guide_list.value[child_name_idx].files.push(article);
                    guide_list.value[child_name_idx].index =
                        Math.min(guide_list.value[child_name_idx].index, index_i);
                } else {
                    guide_list.value.push({
                        index: index_i,
                        name: child_name_i,
                        files: [article],
                    })
                }
            } else if (labels.includes("技术")) {
                const child_name_idx = tech_list.value.findIndex((v) => {
                    return v.name == child_name_i
                })

                if (child_name_idx >= 0) {
                    tech_list.value[child_name_idx].files.push(article);
                    tech_list.value[child_name_idx].index =
                        Math.min(tech_list.value[child_name_idx].index, index_i);
                } else {
                    tech_list.value.push({
                        index: index_i,
                        name: child_name_i,
                        files: [article],
                    })
                }
            } else if (labels.includes("其他")) {
                const child_name_idx = other_list.value.findIndex((v) => {
                    return v.name == child_name_i
                })
                if (child_name_idx >= 0) {
                    other_list.value[child_name_idx].files.push(article);
                    other_list.value[child_name_idx].index =
                        Math.min(other_list.value[child_name_idx].index, index_i);
                } else {
                    other_list.value.push({
                        index: index_i,
                        name: child_name_i,
                        files: [article],
                    })
                }
            }
        }
        // 数组push、pop、shift、unshift、splice、sort、reverse都是响应式的
        notice_list.value.sort((a, b) => { return a.index - b.index });
        guide_list.value.sort((a, b) => { return a.index - b.index });
        tech_list.value.sort((a, b) => { return a.index - b.index });
        other_list.value.sort((a, b) => { return a.index - b.index });
        // console.log(notice_list.value);
        // console.log(guide_list.value);
        // console.log(tech_list.value);
        // console.log(other_list.value);




        const cover = notice_list.value[0].files[0];

        show_article(cover);
    })

})


// 按文章名显示文章
const show_article = (name: string) => {
    if (name.slice(-3) == ".md") {
        proxy.$axios.get('/media/article/' + name
        ).then(function (response) {
            content.value = response.data;
        })
    } else {
        proxy.$axios.get('/media/article/' + name + "/a.md"
        ).then(function (response) {
            // 全局替换图片url
            // 举例：'任意文字![说明](url.jpg "标题")任意文字' 
            // -> '任意文字![说明](http://127.0.0.1/media/article/url.jpg "标题")任意文字'
            content.value = (response.data as string).replaceAll(/(?<=(\!\[[^(\])]*\]\())([^(\s|\))]*)/g,
                process.env.VUE_APP_BASE_API + '/media/article/' + name + '/$2');
        })
    }
}

// 按菜单的索引显示文章，点击菜单的回调
const show_content = (key: string, keyPath: string[]) => {
    const keys = key.split("-");
    if (keys[0] == "1") {
        if (keys.length == 2) {
            show_article(notice_list.value[+keys[1] - 1].files[0]);
        } else if (keys.length == 3) {
            show_article(notice_list.value[+keys[1] - 1].files[+keys[2] - 1]);
        }
    } else if (keys[0] == "2") {
        if (keys.length == 2) {
            show_article(guide_list.value[+keys[1] - 1].files[0]);
        } else if (keys.length == 3) {
            show_article(guide_list.value[+keys[1] - 1].files[+keys[2] - 1]);
        }
    } else if (keys[0] == "3") {
        if (keys.length == 2) {
            show_article(tech_list.value[+keys[1] - 1].files[0]);
        } else if (keys.length == 3) {
            show_article(tech_list.value[+keys[1] - 1].files[+keys[2] - 1]);
        }
    } else if (keys[0] == "4") {
        if (keys.length == 2) {
            show_article(other_list.value[+keys[1] - 1].files[0]);
        } else if (keys.length == 3) {
            show_article(other_list.value[+keys[1] - 1].files[+keys[2] - 1]);
        }
    }
}


</script>
<style lang="css" scoped>
/* 引用块的样式 */
:deep(blockquote) {
    display: block;
    padding-left: 16px;
    padding-right: 16px;
    margin: 0 0 24px;
    border-left: 6px solid #79B6DF;
    background-color: hsl(220, 21%, 95%);
    overflow: auto;
    word-break: normal;
    border-radius: 5px;
}
a{
    cursor: pointer;
}
:deep(a):hover{
    color: #449cd6;
}

/* 代码块的样式 */
:deep(code) {
    border-radius: 5px;
    border: #bbb 1px solid;
    background-color: #efefef;
    overflow: auto;
}
</style>