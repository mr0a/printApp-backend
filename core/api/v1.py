from fastapi import APIRouter


router = APIRouter()


@router.post("/")
async def create_print_order(order_id):
    return "Created Print Order" + order_id


@router.delete("/{order_id}")
async def delete_print_order(order_id: int):
    return "Deleted Print Order" + order_id


@router.post("/{order_id}/completed")
async def complete_print_order(order_id):
    return "Completed Print Order" + order_id


@router.post("/{order_id}/rejected")
async def reject_print_order(order_id):
    return "Rejected Print Order" + order_id


@router.get("/{order_id}")
async def get_print_order(order_id: int):
    return "Print Order" + order_id

