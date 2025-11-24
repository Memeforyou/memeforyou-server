from prisma import Prisma, register
from prisma.models import tag, image, embedding
from apps.ai.utils.schema import ImageTrivial
from typing import List

db = Prisma()
register(db)

# --- async ---
async def get_meta(inputs: List[int]) -> List[ImageTrivial]:

    await db.connect()

    rets = []

    for id in inputs:

        i_image = await db.image.find_unique(
            where={
                'image_id': id
            }
        )

        t_image = ImageTrivial(image_id=i_image['image_id'], caption=i_image['caption'])
        rets.append(t_image)

    return rets