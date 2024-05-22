<template>
    <el-row class="tac">
        <el-col :span="4">
            <h5 class="mb-2">目录</h5>
            <el-menu default-active="2" class="el-menu-vertical-demo">
                <el-sub-menu index="1">
                    <template #title>
                        <el-icon>
                            <location />
                        </el-icon>
                        <span>Navigator One</span>
                    </template>
                    <el-menu-item-group title="Group One">
                        <el-menu-item index="1-1">item one</el-menu-item>
                        <el-menu-item index="1-2">item two</el-menu-item>
                    </el-menu-item-group>
                    <el-menu-item-group title="Group Two">
                        <el-menu-item index="1-3">item three</el-menu-item>
                    </el-menu-item-group>
                    <el-sub-menu index="1-4">
                        <template #title>item four</template>
                        <el-menu-item index="1-4-1">item one</el-menu-item>
                    </el-sub-menu>
                </el-sub-menu>
                <el-menu-item index="2">
                    <el-icon><icon-menu /></el-icon>
                    <span>Navigator Two</span>
                </el-menu-item>
                <el-menu-item index="3" disabled>
                    <el-icon>
                        <document />
                    </el-icon>
                    <span>Navigator Three</span>
                </el-menu-item>
                <el-menu-item index="4">
                    <el-icon>
                        <setting />
                    </el-icon>
                    <span>Navigator Four</span>
                </el-menu-item>
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


onMounted(() => {
    proxy.$axios.get('/article/articles/'
    ).then(function (response) {
        console.log(response.data[1]);
        const articles = response.data;
        const cover = response.data[1];

        if (cover.slice(-3) == ".md") {
            proxy.$axios.get('/static/article/' + cover
            ).then(function (response) {
                content.value = response.data;
                console.log(content.value);

            })
        } else {
            proxy.$axios.get('/static/' + cover + "/a.md"
            ).then(function (response) {
                content.value = response.data;
                console.log(content.value);

            })
        }
    })

})

</script>
<style></style>