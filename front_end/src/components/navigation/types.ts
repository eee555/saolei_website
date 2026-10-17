export interface NavigationItem {
    id: string;
    label: string;
    icon?: string;
    iconOnly?: boolean;
    primary?: boolean;
    to?: string;
    href?: string;
    target?: '_blank';
    action?: () => void | Promise<void>;
    children?: NavigationItem[];
    checked?: boolean;
    testId?: string;
}
