
export function validateSuccess(elFormItemRef: any) {
    elFormItemRef.value!.validateMessage = '';
    elFormItemRef.value!.validateState = 'success';
}
export function validateError(elFormItemRef: any, msg: string) {
    elFormItemRef.value!.validateMessage = msg;
    elFormItemRef.value!.validateState = 'error';
}
