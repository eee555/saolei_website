from ninja import Router

from .pb.api import router as pb_router
from .saolei.api import router as saolei_router

router = Router()
router.add_router('', saolei_router)
router.add_router('/pb', pb_router)
