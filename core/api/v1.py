from fastapi import APIRouter, Request, HTTPException
from ..schemas import OrderBase, FileConfigBase
from app.database import Order, FileConfig, File, Repro, database


router = APIRouter()

@router.get("/{order_id}")
async def get_print_order(request: Request, order_id: int):
    order = await Order.objects.get_or_none(user=request.user, pk=order_id)
    if order is None:
        raise HTTPException(404, "Order Not Found")
    return order


@router.get("/", response_model=list[Order])
async def get_all_orders(request: Request):
    orders = await Order.objects.all(user=request.user.id)
    for order in orders:
        # print(order)
        print("Order: ", order.id, await FileConfig.objects.all(order=order.id))
    return orders

@router.post("/")
async def create_print_order(request: Request, payload: OrderBase):
    reprography = await Repro.objects.get_or_none(username=payload.repro)
    if reprography is None:
        raise HTTPException(404, "Reprography not found")
    # transaction = await database.transaction()
    # await transaction.start()
    try:
        createdOrder = Order(user=request.user.id, repro=reprography,
                         payment_method=payload.payment_method, total_amount=payload.total_amount,
                         status="Draft")
        await createdOrder.save()
        print("Create Order: ", createdOrder)
        files = []
        for fileConfig in payload.files:
            print(fileConfig)
            file = await File.objects.get_or_none(owner=request.user.id, pk=fileConfig.file_id)
            if file is None:
                raise HTTPException(404, "File Not Found")
            # config = await FileConfig.objects.create(file=file, sheet_size=fileConfig.sheetSize, page_selection="All")
            # createdOrder.order_files.append(config)
            await createdOrder.files.add(file, sheet_size=fileConfig.sheetSize, page_selection="All")
            # files.append(config)
        # await createdOrder.update(order_files = files)
        # await createdOrder.update()
        print(createdOrder)
        # breakpoint()
        # await createdOrder.save()
    except Exception as e:
        print("Some error occurred")
        # await transaction.rollback()
        raise e
    else:
        # await transaction.commit()
        print(payload)
        return "Created Print Order"


@router.delete("/{order_id}")
async def delete_print_order(request: Request, order_id: int):
    deleted = Order.objects.delete(user=request.user, pk=order_id)
    if deleted == 0:
        raise HTTPException(404, "Order Not Found")
    return "Deleted Print Order" + order_id


@router.get("/{order_id}/status")
async def get_order_status(order_id):
    return "Completed or Pending or Rejected"


@router.post("/{order_id}/status")
async def complete_print_order(order_id):
    return "Completed Print Order" + order_id



