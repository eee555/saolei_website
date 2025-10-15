from .models import TournamentParticipant

def participant_videos(participant: TournamentParticipant):
    return list(participant.videos.values('id', 'upload_time', "level", "mode", "timems", "bv", "state", "software", "cl", "ce", "file_size", "end_time", 'path'))
