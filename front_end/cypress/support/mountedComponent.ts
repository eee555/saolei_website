interface MountedComponent {
    unmount: () => void;
}

let mountedComponent: MountedComponent | null = null;

export function setMountedComponent(component: MountedComponent): void {
    mountedComponent = component;
}

export function unmountMountedComponent(): void {
    if (mountedComponent === null) return;
    mountedComponent.unmount();
    mountedComponent = null;
}
