<template>
    <el-form :model="form">
        <el-form-item label="ID">
            <el-input type="number" v-model="form.id"/>
        </el-form-item>
        <el-form-item label="平台">
            <el-select v-model="form.platform">
                <el-option v-for="(item, key) of platformlist" :label="item.name" :value="key"></el-option>
            </el-select>
        </el-form-item>
        <el-form-item label="平台ID">
            <el-input v-model="form.identifier"></el-input>
        </el-form-item>
        <el-form-item>
            <el-button @click="verify">绑定</el-button>
            <el-button @click="unverify">解绑</el-button>
        </el-form-item>
    </el-form>
</template>

<script setup lang="ts">
import { platformlist } from '@/utils/common/accountLinkPlatforms';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { reactive } from 'vue';
import { httpErrorNotification } from '../Notifications';

const { proxy } = useCurrentInstance();

const form = reactive({
    id: 0,
    platform: '',
    identifier: '',
});

const verify = () => {
    proxy.$axios.post('accountlink/verify/',
        {
            id: form.id,
            platform: form.platform,
            identifier: form.identifier,
        }
    ).then(function (response) {
        form.id = 0;
        form.platform = '';
        form.identifier = '';
    }).catch(httpErrorNotification)
}

const unverify = () => {
    proxy.$axios.post('accountlink/unverify/',
        {
            id: form.id,
            platform: form.platform,
            identifier: form.identifier,
        }
    ).then(function (response) {
        form.id = 0;
        form.platform = '';
        form.identifier = '';
    }).catch(httpErrorNotification)
}

</script>