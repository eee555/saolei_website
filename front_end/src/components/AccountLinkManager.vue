<template>
    <el-table :data="accountlinks">
        <el-table-column :label="$t('accountlink.platform')">
            <template #default="scope">
                <PlatformIcon :platform="scope.row.platform"/>
            </template>
        </el-table-column>
        <el-table-column label="ID">
            <template #default="scope">
                <el-link v-if="scope.row.platform == 'a'" :href="'https://minesweepergame.com/profile.php?pid=' + scope.row.identifier" target="_blank">{{ scope.row.identifier }}</el-link>
                <el-link v-else-if="scope.row.platform == 'c'" :href="'http://saolei.wang/Player/Index.asp?Id=' + scope.row.identifier" target="_blank">{{ scope.row.identifier }}</el-link>
                <el-link v-else-if="scope.row.platform == 'w'" :href="'https://minesweeper.online/player/' + scope.row.identifier" target="_blank">{{ scope.row.identifier }}</el-link>
                <el-text v-else>{{ scope.row.identifier }}</el-text>
            </template>
        </el-table-column>
        <el-table-column v-if="store.player.id==store.user.id" :label="$t('common.prop.status')">
            <template #default="scope">
                <el-tooltip v-if="scope.row.verified" :content="$t('accountlink.verified')">
                    <el-text type="success"><el-icon><CircleCheck/></el-icon></el-text>
                </el-tooltip>
                <el-tooltip v-else :content="$t('accountlink.unverified')">
                    <el-text><el-icon><Clock/></el-icon></el-text>
                </el-tooltip>
            </template>
        </el-table-column>
        <el-table-column v-if="store.player.id==store.user.id" :label="$t('common.prop.action')">
            <template #default="scope">
                <el-link :underline="false" @click.prevent="deleteRow(scope.$index)"><el-icon>
                        <Delete />
                    </el-icon></el-link>
            </template>
        </el-table-column>
    </el-table>
    <el-button v-if="store.player.id==store.user.id" style="width:100%" @click="formvisible = true">
        <el-icon>
            <Plus />
        </el-icon>
    </el-button>
    <el-dialog v-model="formvisible" :title="$t('accountlink.addLink')" @closed="form.platform = ''; form.identifier = '';" width="500px">
        <el-form :model="form">
            <el-form-item :label="$t('accountlink.platform')">
                <el-select v-model="form.platform">
                    <el-option v-for="item in platformlist" :value="item.key" :label="item.name" :disabled="userHasPlatform(item.key)"/>
                </el-select>
            </el-form-item>
            <el-form-item label="ID">
                <el-input v-model="form.identifier" maxlength="128" />
            </el-form-item>
            <el-form-item v-if="form.platform == 'c'">
                <el-text>
                    <b>{{ $t('accountlink.guideTitle') }}</b><br />
                    {{ $t('accountlink.guideSaolei1') }}<PlatformIcon platform="c"/>{{ $t('accountlink.guideSaolei2') }}<br />
                    <img src="../assets/IdGuideSaolei.png" width="100%" />
                </el-text>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" :disabled="!formValid"
                    @click.prevent="addLink(); formvisible = false;">{{ $t('common.button.confirm') }}</el-button>
                <el-button @click.prevent="formvisible = false">{{ $t('common.button.cancel') }}</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script setup lang="ts">

import { computed, onMounted, reactive, ref } from 'vue';
import useCurrentInstance from '@/utils/common/useCurrentInstance';
import { useUserStore } from '@/store';
import { Action, ElMessageBox } from 'element-plus';
import { platformlist } from '@/utils/common/accountLinkPlatforms'
import PlatformIcon from './widgets/PlatformIcon.vue';
import { useI18n } from 'vue-i18n';

interface AccountLink {
    platform: string;
    identifier: string;
    verified: boolean;
}

const { proxy } = useCurrentInstance();
const t = useI18n();
const store = useUserStore();
const accountlinks = ref<AccountLink[]>([]);
const formvisible = ref(false);
const form = reactive({
    platform: '',
    identifier: '',
})

const refresh = () => {
    proxy.$axios.get('accountlink/get/',
        {
            params: {
                id: store.player.id
            }
        }
    ).then(function (response) {
        accountlinks.value = response.data;
    })
}
onMounted(refresh)

const formValid = computed(() => {
    switch (form.platform) {
        case 'c':
            const num = parseInt(form.identifier, 10);
            return !isNaN(num) && num.toString() === form.identifier && num > 0
        default:
            return false;
    }
})

const addLink = () => {
    proxy.$axios.post('accountlink/add/',
        {
            platform: form.platform,
            identifier: form.identifier,
        }
    ).then(function (response) {
        refresh()
    })
}

const deleteRow = (index: number) => {
    ElMessageBox.confirm(accountlinks.value[index]+'', t.t('accountlink.deleteLinkMessage')).then(() => {
        proxy.$axios.post('accountlink/delete/', { platform: accountlinks.value[index].platform }).then(function (response) {
            refresh()
        })
    }).catch(() => { })
}

const userHasPlatform = (platform: string) => {
    for (let item of accountlinks.value) {
        if (item.platform == platform) return true;
    }
    return false;
}

</script>