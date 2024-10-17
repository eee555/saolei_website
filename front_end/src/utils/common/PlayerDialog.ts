import { videoplayerstore } from "@/store";

export const preview = (id: number | undefined) => {
    if (!id) {
        return;
    }
    videoplayerstore.id = id;
    videoplayerstore.visible = true;
}