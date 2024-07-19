import { useVideoPlayerStore } from "@/store";

const videoplayerstore = useVideoPlayerStore();

export const preview = (id: number | undefined) => {
    if (!id) {
        return;
    }
    videoplayerstore.id = id;
    videoplayerstore.visible = true;
}