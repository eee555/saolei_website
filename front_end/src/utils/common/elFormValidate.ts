import type { FormItemInstance } from 'element-plus';
import type { ShallowRef } from 'vue';

type FormItemRef = Readonly<ShallowRef<FormItemInstance | null>>;

export function validateSuccess(elFormItemRef: FormItemRef): void {
    if (elFormItemRef.value === null) return;
    elFormItemRef.value.validateMessage = '';
    elFormItemRef.value.validateState = 'success';
}
export function validateError(elFormItemRef: FormItemRef, msg: string): void {
    if (elFormItemRef.value === null) return;
    elFormItemRef.value.validateMessage = msg;
    elFormItemRef.value.validateState = 'error';
}
