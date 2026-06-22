import eslint from '@eslint/js';
import stylistic from '@stylistic/eslint-plugin';
import { defineConfig } from 'eslint/config';
import pluginCypress from 'eslint-plugin-cypress';
import importPlugin from 'eslint-plugin-import';
import pluginVue from 'eslint-plugin-vue';
import globals from 'globals';
import tseslint from 'typescript-eslint';
// import vueI18n from '@intlify/eslint-plugin-vue-i18n'; // 不兼容ts。https://github.com/intlify/eslint-plugin-vue-i18n/issues/32

export default defineConfig({
    files: ['**/*.{js,ts,vue}'],
    ignores: [
        '**/node_modules/**', '**/dist/**', '**/build/**', '**/public/**',
        '**/GuideView.vue', '**/WorldView.vue',
    ],
    plugins: {
        '@stylistic': stylistic,
        cypress: pluginCypress,
    },
    extends: [
        eslint.configs.recommended,
        importPlugin.flatConfigs.recommended,
        tseslint.configs.all,
        ...pluginVue.configs['flat/recommended'],
        pluginCypress.configs.recommended,
        stylistic.configs.all,
        // ...vueI18n.configs.recommended, // 不兼容ts。https://github.com/intlify/eslint-plugin-vue-i18n/issues/32
    ],
    languageOptions: {
        globals: {
            ...globals.browser,
            ...pluginCypress.configs.recommended.globals,
        },
        parserOptions: {
            parser: tseslint.parser,
            projectService: true,
            extraFileExtensions: ['.vue'],
        },
    },
    rules: {
        'import/consistent-type-specifier-style': 'error',
        'import/extensions': 'error',
        'import/first': 'error',
        'import/newline-after-import': 'error',
        'import/no-absolute-path': 'error',
        'import/no-cycle': 'error',
        'import/no-duplicates': 'error',
        'import/no-dynamic-require': 'error',
        'import/no-relative-packages': 'error',
        'import/no-restricted-paths': 'error',
        'import/no-self-import': 'error',
        'import/no-unused-modules': 'error',
        'import/no-useless-path-segments': 'error',
        'import/no-webpack-loader-syntax': 'error',
        'import/order': [
            'error', {
                'newlines-between': 'always',
                alphabetize: {
                    order: 'asc',
                    caseInsensitive: true,
                },
                named: true,
            },
        ],
        'no-control-regex': 'off',
        'no-irregular-whitespace': 'off',
        'no-prototype-builtins': 'off',
        'vue/block-lang': ['error', { script: { lang: 'ts' } }],
        'vue/block-order': ['error', { order: ['template', 'script', 'style'] }],
        'vue/block-tag-newline': 'error',
        'vue/component-api-style': ['error', ['script-setup']],
        'vue/component-name-in-template-casing': 'error',
        'vue/component-options-name-casing': 'error',
        // 'vue/custom-event-name-casing': 'error',
        // 'vue/define-emits-declaration': 'error',
        'vue/define-macros-order': 'error',
        'vue/define-props-declaration': ['error', 'runtime'],
        'vue/define-props-destructuring': ['error', { destructure: 'never' }],
        // vue/enforce-style-attribute
        'vue/first-attribute-linebreak': 'error',
        'vue/html-closing-bracket-newline': 'error',
        'vue/html-closing-bracket-spacing': 'error',
        'vue/html-comment-content-newline': ['error', { multiline: 'never' }],
        'vue/html-comment-content-spacing': 'error',
        // 'vue/html-comment-indent': ['error', 4],
        'vue/html-indent': ['error', 4],
        'vue/html-quotes': ['error', 'double'],
        // vue/match-component-file-name
        // vue/match-component-import-name
        'vue/max-attributes-per-line': 'off', // 属性长度差别很大
        'vue/multi-word-component-names': 'off',
        'vue/no-duplicate-class-names': 'error',
        'vue/no-empty-component-block': 'error',
        'vue/no-import-compiler-macros': 'error',
        'vue/no-irregular-whitespace': ['error', { skipHTMLTextContents: true }],
        // vue/no-literals-in-template
        'vue/no-multiple-objects-in-class': 'error',
        // vue/no-negated-v-if-condition
        // vue/no-potential-component-option-typo
        // vue/no-ref-object-reactivity-loss
        // vue/no-restricted-block
        // vue/no-restricted-call-after-await
        // vue/no-restricted-class
        // vue/no-restricted-component-names
        // vue/no-restricted-component-options
        // vue/no-restricted-custom-event
        'vue/no-restricted-html-elements': [
            'error', {
                element: ['ElText', 'el-text'],
                message: 'Use "@/styles/text.css" instead.',
            },
        ],
        // vue/no-restricted-props
        // vue/no-restricted-static-attribute
        // vue/no-restricted-v-bind
        // vue/no-restricted-v-on
        // 'vue/no-root-v-if': 'error',
        // vue/no-setup-props-reactivity-loss
        // vue/no-static-inline-styles
        'vue/no-template-shadow': 'off',
        'vue/no-template-target-blank': 'error',
        // vue/no-this-in-before-route-enter
        'vue/no-undef-components': [
            'error', { ignorePatterns: [
                'ArrowLeft',
                'ArrowRight',
                'Check',
                'Ticket',
                'QuestionFilled',
                'router-view',
            ] },
        ],
        'vue/no-undef-directives': 'error',
        'vue/no-undef-properties': 'error',
        'vue/no-unsupported-features': ['error', { version: '^3.5.0' }],
        'vue/no-unused-emit-declarations': 'error',
        'vue/no-unused-properties': 'error',
        'vue/no-unused-refs': 'error',
        'vue/no-use-v-else-with-v-for': 'error',
        'vue/no-useless-mustaches': 'error',
        'vue/no-useless-v-bind': 'error',
        'vue/no-v-text': 'error',
        'vue/padding-line-between-blocks': 'error',
        'vue/padding-line-between-tags': 'off',
        // vue/padding-lines-in-component-definition
        'vue/prefer-define-options': 'error',
        'vue/prefer-prop-type-boolean-first': 'error',
        'vue/prefer-separate-static-class': 'error',
        'vue/prefer-single-event-payload': 'off',
        'vue/prefer-template': 'error',
        'vue/prefer-true-attribute-shorthand': 'error',
        'vue/prefer-use-template-ref': 'error',
        'vue/prefer-v-model': 'error',
        // vue/require-default-export
        // vue/require-direct-export
        // vue/require-emit-validator
        // 'vue/require-explicit-slots': 'error',  // TODO
        'vue/require-expose': 'error',
        'vue/require-macro-variable-name': 'error',
        // vue/require-name-property
        'vue/require-prop-comment': 'off',
        'vue/require-typed-object-prop': 'error',
        'vue/require-typed-ref': 'error',
        'vue/require-v-for-key': 'off',
        'vue/restricted-component-names': 'off',
        'vue/singleline-html-element-content-newline': 'error',
        'vue/slot-name-casing': 'error',
        'vue/sort-keys': 'off',
        'vue/static-class-names-order': 'error',
        '@stylistic/array-bracket-newline': ['error', 'consistent'],
        '@stylistic/array-element-newline': 'off',
        '@stylistic/comma-dangle': ['error', 'always-multiline'],
        '@stylistic/function-call-argument-newline': ['error', 'consistent'],
        '@stylistic/function-paren-newline': ['error', 'consistent'],
        '@stylistic/indent-binary-ops': ['error', 4],
        '@stylistic/linebreak-style': 'off',
        '@stylistic/lines-around-comment': ['error', {
            beforeBlockComment: true,
            allowClassStart: true,
            allowInterfaceStart: true,
            allowTypeStart: true,
        }],
        '@stylistic/lines-between-class-members': ['error', {
            enforce: [
                { blankLine: 'never', prev: 'field', next: 'field' },
                { blankLine: 'always', prev: 'method', next: 'method' },
            ],
        }],
        '@stylistic/multiline-comment-style': 'off',
        '@stylistic/multiline-ternary': ['error', 'always-multiline'],
        '@stylistic/newline-per-chained-call': 'off',
        '@stylistic/no-extra-parens': ['error', 'all', {
            enforceForArrowConditionals: false,
        }],
        '@stylistic/no-multiple-empty-lines': ['error', { max: 1 }],
        '@stylistic/object-curly-spacing': ['error', 'always'],
        '@stylistic/object-property-newline': ['error', { allowAllPropertiesOnSameLine: true }],
        '@stylistic/operator-linebreak': ['error', 'before'],
        '@stylistic/padded-blocks': ['error', 'never'],
        '@stylistic/quote-props': ['error', 'as-needed'],
        '@stylistic/quotes': ['error', 'single'],
        '@stylistic/space-before-function-paren': ['error', {
            anonymous: 'always',
            named: 'never',
        }],

        '@typescript-eslint/explicit-function-return-type': 'off', // 和i18n冲突
        '@typescript-eslint/promise-function-async': 'off', // 和Vue Router、defineAsyncComponent冲突
        '@typescript-eslint/naming-convention': 'off', // TODO：涉及到前后端标准不一致的问题，很复杂
        '@typescript-eslint/no-explicit-any': 'off', // TODO
        '@typescript-eslint/no-magic-numbers': 'off', // TODO
        '@typescript-eslint/no-unsafe-argument': 'off', // TODO：牵扯到的内容很多，包括后端API重构等
        '@typescript-eslint/no-unsafe-assignment': 'off', // TODO：牵扯到的内容很多，包括后端API重构等
        '@typescript-eslint/no-unsafe-member-access': 'off', // TODO：牵扯到的内容很多，包括后端API重构等
        '@typescript-eslint/no-unsafe-type-assertion': 'off', // 和Vue的PropType冲突
        '@typescript-eslint/no-use-before-define': 'off', // 为了代码可读性，有的函数需要放在最后
        '@typescript-eslint/prefer-readonly-parameter-types': 'off',
    },
    settings: {
        'vue-i18n': {
            localeDir: 'src/i18n/locales/*.ts',
            messageSyntaxVersion: '^11.0.0',
        },
        'import/resolver': {
            // You will also need to install and configure the TypeScript resolver
            // See also https://github.com/import-js/eslint-import-resolver-typescript#configuration
            typescript: true,
            node: true,
        },
    },
}, {
    files: ['**/*.cy.ts'],
    rules: {
        '@typescript-eslint/no-unused-expressions': 'off',
    },
});
