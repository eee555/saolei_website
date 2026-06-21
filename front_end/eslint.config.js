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
    ignores: ['**/node_modules/**', '**/dist/**', '**/build/**', '**/GuideView.vue', '**/public/**'],
    plugins: {
        '@stylistic': stylistic,
        'cypress': pluginCypress,
    },
    extends: [
        eslint.configs.recommended,
        importPlugin.flatConfigs.recommended,
        tseslint.configs.recommended,
        ...pluginVue.configs['flat/recommended'],
        pluginCypress.configs.recommended,
        // ...vueI18n.configs.recommended, // 不兼容ts。https://github.com/intlify/eslint-plugin-vue-i18n/issues/32
    ],
    languageOptions: {
        globals: {
            ...globals.browser,
            ...pluginCypress.configs.recommended.globals,
        },
        parserOptions: {
            parser: tseslint.parser,
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
                'alphabetize': {
                    'order': 'asc',
                    'caseInsensitive': true,
                },
                'named': true,
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
        'vue/no-irregular-whitespace': ['error', { 'skipHTMLTextContents': true }],
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
        '@stylistic/array-bracket-newline': 'error',
        '@stylistic/array-bracket-spacing': 'error',
        // @stylistic/array-element-newline
        '@stylistic/arrow-parens': 'error',
        '@stylistic/arrow-spacing': 'error',
        '@stylistic/block-spacing': 'error',
        '@stylistic/brace-style': ['error', '1tbs', { 'allowSingleLine': true }],
        '@stylistic/comma-dangle': ['error', 'always-multiline'],
        '@stylistic/comma-spacing': 'error',
        '@stylistic/comma-style': 'error',
        '@stylistic/computed-property-spacing': 'error',
        '@stylistic/curly-newline': ['error', { 'consistent': true }],
        '@stylistic/dot-location': 'error',
        '@stylistic/eol-last': 'error',
        '@stylistic/function-call-spacing': 'error',
        '@stylistic/generator-star-spacing': 'error',
        '@stylistic/implicit-arrow-linebreak': 'error',
        '@stylistic/indent': ['error', 4],
        '@stylistic/indent-binary-ops': ['error', 4],
        '@stylistic/key-spacing': 'error',
        '@stylistic/keyword-spacing': 'error',
        '@stylistic/member-delimiter-style': 'error',
        '@stylistic/new-parens': 'error',
        '@stylistic/newline-per-chained-call': 'off', // 不兼容代码风格
        '@stylistic/no-extra-parens': 'off', // 有些一元运算符需要括号保持可读性
        '@stylistic/no-extra-semi': 'error',
        '@stylistic/no-floating-decimal': 'error',
        '@stylistic/no-mixed-operators': 'off', // 加法和乘法还是不需要括号的
        '@stylistic/no-mixed-spaces-and-tabs': 'error',
        '@stylistic/no-multi-spaces': ['error', { 'ignoreEOLComments': true }],
        '@stylistic/no-trailing-spaces': 'error',
        '@stylistic/no-whitespace-before-property': 'error',
        '@stylistic/nonblock-statement-body-position': 'error',
        '@stylistic/object-curly-newline': ['error', { 'consistent': true }],
        '@stylistic/object-curly-spacing': ['error', 'always'],
        '@stylistic/padded-blocks': ['error', 'never'],
        '@stylistic/quotes': ['error', 'single'],
        '@stylistic/rest-spread-spacing': 'error',
        '@stylistic/semi': 'error',
        '@stylistic/semi-spacing': 'error',
        '@stylistic/semi-style': 'error',
        '@stylistic/space-before-blocks': 'error',
        '@stylistic/space-before-function-paren': ['error', { 'named': 'never' }],
        '@stylistic/space-in-parens': 'error',
        '@stylistic/space-infix-ops': 'error',
        '@stylistic/space-unary-ops': 'error',
        '@stylistic/spaced-comment': 'error',
        '@stylistic/switch-colon-spacing': 'error',
        '@stylistic/template-curly-spacing': 'error',
        '@stylistic/template-tag-spacing': 'error',
        '@stylistic/type-annotation-spacing': 'error',
        '@stylistic/type-generic-spacing': 'error',
        '@stylistic/type-named-tuple-spacing': 'error',
        '@stylistic/wrap-regex': 'error',
        '@stylistic/yield-star-spacing': 'error',
        '@typescript-eslint/ban-ts-comment': 'off',
        '@typescript-eslint/no-empty-object-type': 'off',
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-namespace': 'off',
        '@typescript-eslint/no-unsafe-function-type': 'off',
        '@typescript-eslint/no-unused-expressions': 'off',
        '@typescript-eslint/no-unused-vars': ['error', { 'argsIgnorePattern': '^_', 'caughtErrorsIgnorePattern': '^_' }],
    },
    settings: {
        'vue-i18n': {
            localeDir: 'src/i18n/locales/*.ts',
            messageSyntaxVersion: '^11.0.0',
        },
        'import/resolver': {
            // You will also need to install and configure the TypeScript resolver
            // See also https://github.com/import-js/eslint-import-resolver-typescript#configuration
            'typescript': true,
            'node': true,
        },
    },
});
