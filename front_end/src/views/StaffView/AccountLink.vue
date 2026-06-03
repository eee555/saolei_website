<template>
    <el-form :model="form">
        <el-form-item label="ID">
            <el-input v-model="form.id" type="number" />
        </el-form-item>
        <el-form-item label="平台">
            <el-select v-model="form.platform">
                <el-option v-for="(item, key) of platformlist" :key="key" :label="item.name" :value="key" />
            </el-select>
        </el-form-item>
        <el-form-item label="平台ID">
            <el-input v-model="form.identifier" />
        </el-form-item>
        <el-form-item>
            <el-button @click="verify">
                绑定
            </el-button>
            <el-button @click="unverify">
                解绑
            </el-button>
        </el-form-item>
    </el-form>
    <PrDataTable
        v-loading="loading"
        :value="accountLinks"
        row-hover
        size="small"
        paginator
        :rows="10"
        :rows-per-page-options="[10, 25, 50, 100]"
        paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown JumpToPageInput CurrentPageReport"
    >
        <PrColumn field="userprofile" header="User ID" sortable />
        <PrColumn field="platform" header="Platform" sortable>
            <template #body="{ data }: { data: AccountLinkQueueItem }">
                {{ platformlist[data.platform]?.name ?? data.platform }}
            </template>
        </PrColumn>
        <PrColumn field="identifier" header="Platform ID" sortable />
        <PrColumn field="verified" header="Verified" sortable />
    </PrDataTable>
</template>

<script setup lang="ts">
import { ElButton, ElForm, ElFormItem, ElInput, ElOption, ElSelect, vLoading } from 'element-plus';
import PrColumn from 'primevue/column';
import PrDataTable from 'primevue/datatable';
import { onMounted, reactive, ref } from 'vue';

import { httpErrorNotification } from '@/components/Notifications';
import { Platform, platformlist } from '@/utils/common/accountLinkPlatforms';
import useCurrentInstance from '@/utils/common/useCurrentInstance';

const { proxy } = useCurrentInstance();

interface AccountLinkQueueItem {
    id: number | null;
    platform: Platform;
    identifier: string;
    userprofile: number;
    verified: boolean;
}

const form = reactive({
    id: 0,
    platform: '',
    identifier: '',
});

const accountLinks = ref<AccountLinkQueueItem[]>([]);
const loading = ref(false);

const refresh = async () => {
    loading.value = true;
    await proxy.$axios.get('/api/accountlink/admin/queue').then((response) => {
        accountLinks.value = response.data;
    }).catch(httpErrorNotification);
    loading.value = false;
};

const verify = () => {
    proxy.$axios.post('accountlink/verify/',
        {
            id: form.id,
            platform: form.platform,
            identifier: form.identifier,
        },
    ).then(function (_response) {
        form.id = 0;
        form.platform = '';
        form.identifier = '';
        refresh();
    }).catch(httpErrorNotification);
};

const unverify = () => {
    proxy.$axios.post('accountlink/unverify/',
        {
            id: form.id,
            platform: form.platform,
            identifier: form.identifier,
        },
    ).then(function (_response) {
        form.id = 0;
        form.platform = '';
        form.identifier = '';
        refresh();
    }).catch(httpErrorNotification);
};

onMounted(refresh);
</script>
