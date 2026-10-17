export interface LoginControls {
    open: (form: 'login' | 'register') => void;
    logout: () => Promise<void>;
    labels: { login: string; register: string; logout: string };
}
