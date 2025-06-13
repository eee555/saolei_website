import random
from .models import GSC, GSCParticipant, GSCVideo
from videomanager.models import VideoModel
from config.text_choices import MS_TextChoices

def start_gsc(gsc: GSC):
    gsc.update(token=f"G{random.randint(0, 99999):05d}")


def new_video(video: VideoModel, gsc: GSC):
    participant = GSCParticipant.objects.filter(user=video.player, gsc=gsc).first()
    if not participant:
        participant = GSCParticipant.objects.create(user=video.player, gsc=gsc)

    gscvideo = GSCVideo.objects.create(participant=participant, video=video)

    if gscvideo.level == MS_TextChoices.Level.BEGINNER:
        if gscvideo.timems < participant.bt20th and gscvideo.bv >= 10:
            participant.bt20sum = participant.bt20sum - participant.bt20th + gscvideo.timems
            participant.bt20th = GSCVideo.objects.filter(participant=participant, level=MS_TextChoices.Level.BEGINNER).order_by('timems')[19].timems
        if gscvideo.timems < participant.bt1st and gscvideo.bv >= 10:
            participant.bt1st = gscvideo.timems
    elif gscvideo.level == MS_TextChoices.Level.INTERMEDIATE:
        if gscvideo.timems < participant.it12th:
            participant.it12sum = participant.it12sum - participant.it12th + gscvideo.timems
            participant.it12th = GSCVideo.objects.filter(participant=participant, level=MS_TextChoices.Level.INTERMEDIATE).order_by('timems')[11].timems
        if gscvideo.timems < participant.it1st:
            participant.it1st = gscvideo.timems
    elif gscvideo.level == MS_TextChoices.Level.EXPERT:
        if gscvideo.timems < participant.et5th:
            participant.et5sum = participant.et5sum - participant.et5th + gscvideo.timems
            participant.et5th = GSCVideo.objects.filter(participant=participant, level=MS_TextChoices.Level.EXPERT).order_by('timems')[4].timems
        if gscvideo.timems < participant.et1st:
            participant.et1st = gscvideo.timems

    participant.save()