<template>
    <el-row class="tac">
        <el-col :span="4">
            <h5 class="mb-2">目录</h5>
            <el-menu class="el-menu-vertical">
                <el-sub-menu index="1">
                    <template #title>
                        <el-icon><Document /></el-icon>
                        <span>公告</span>
                    </template>
                    <template v-for="(item, idx) in notice_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`1-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                        </el-menu-item>
                        <el-sub-menu v-else :index="`1-${idx + 1}`">
                            <template #title>{{ item.name }}</template>
                            <template v-for="(i, idy) in item.files">
                                <el-menu-item :index="`1-${idx + 1}-${idy + 1}`">
                                    {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                                </el-menu-item>
                            </template>
                        </el-sub-menu>
                    </template>
                </el-sub-menu>
                <el-sub-menu index="2">
                    <template #title>
                        <el-icon><Guide /></el-icon>
                        <span>教程</span>
                    </template>
                    <template v-for="(item, idx) in guide_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`2-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                        </el-menu-item>
                        <el-sub-menu v-else :index="`2-${idx + 1}`">
                            <template #title>{{ item.name }}</template>
                            <template v-for="(i, idy) in item.files">
                                <el-menu-item :index="`2-${idx + 1}-${idy + 1}`">
                                    {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                                </el-menu-item>
                            </template>
                        </el-sub-menu>
                    </template>
                </el-sub-menu>
                <el-sub-menu index="3">
                    <template #title>
                        <el-icon><Cpu /></el-icon>
                        <span>技术</span>
                    </template>
                    <template v-for="(item, idx) in tech_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`3-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                        </el-menu-item>
                        <el-sub-menu v-else :index="`3-${idx + 1}`">
                            <template #title>{{ item.name }}</template>
                            <template v-for="(i, idy) in item.files">
                                <el-menu-item :index="`3-${idx + 1}-${idy + 1}`">
                                    {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                                </el-menu-item>
                            </template>
                        </el-sub-menu>
                    </template>
                </el-sub-menu>
                <el-sub-menu index="4">
                    <template #title>
                        <el-icon><Grid /></el-icon>
                        <span>其他</span>
                    </template>
                    <template v-for="(item, idx) in other_list">
                        <el-menu-item v-if="item.name[0] == '['" :index="`4-${idx + 1}`">
                            {{ item.files[0].match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                        </el-menu-item>
                        <el-sub-menu v-else :index="`4-${idx + 1}`">
                            <template #title>{{ item.name }}</template>
                            <template v-for="(i, idy) in item.files">
                                <el-menu-item :index="`4-${idx + 1}-${idy + 1}`">
                                    {{ i.match(/(?<=\]).*/)![0].replace(/\.md$/, '') }}
                                </el-menu-item>
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
\`\`\` py
import re
print(777)
\`\`\`

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
 
 \$\{toc\}
 
 ![Image](http://www.saolei.wang/Models/Images/Common/Logo.gif)


 就回国参加

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




        const cover = response.data[0];


        if (cover.slice(-3) == ".md") {
            proxy.$axios.get('/media/article/' + cover
            ).then(function (response) {
                content.value = response.data;
            })
        } else {
            proxy.$axios.get('/media/' + cover + "/a.md"
            ).then(function (response) {
                content.value = response.data;
            })
        }
    })

})

</script>
<style></style>