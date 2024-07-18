import { usePlayerStore } from "@/store";

const playerstore = usePlayerStore();

export const preview = (id: number | undefined) => {
    if (!id) {
        return;
    }
    playerstore.id = id;
    playerstore.visible = true;
}