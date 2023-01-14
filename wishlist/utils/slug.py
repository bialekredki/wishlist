from typing import Callable

from slugify import slugify

from wishlist.database import get_client


async def find_unqiue_slug(resource: str, slug_query: Callable, separator: str = "__"):
    slugified_resource = slugify(resource)
    slug = slugified_resource
    for _ in range(2**10):
        result = await slug_query(get_client(), slug=slug)
        if not result:
            return slug
        slug = f"{slugified_resource}{separator}{_:x}"
    raise RuntimeError(f"Couldn't find a unique slug for resource {resource}")
