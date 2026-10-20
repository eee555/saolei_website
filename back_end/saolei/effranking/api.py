from ninja import Router

from .thrp.api import router as thrp_router

router = Router()
router.add_router('/thrp', thrp_router)
