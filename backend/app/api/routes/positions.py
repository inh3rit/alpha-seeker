from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import PositionCreate, PositionResponse, PositionUpdate
from app.models.position import UserPosition

router = APIRouter()


@router.get("", response_model=list[PositionResponse])
def list_positions(db: Session = Depends(get_db)):
    """获取持仓列表"""
    return db.query(UserPosition).filter(UserPosition.status == "holding").all()


@router.post("", response_model=PositionResponse, status_code=201)
def create_position(data: PositionCreate, db: Session = Depends(get_db)):
    """添加持仓"""
    pos = UserPosition(
        code=data.code,
        buy_date=data.buy_date,
        buy_price=data.buy_price,
        quantity=data.quantity,
    )
    db.add(pos)
    db.commit()
    db.refresh(pos)
    return pos


@router.put("/{position_id}", response_model=PositionResponse)
def update_position(position_id: int, data: PositionUpdate, db: Session = Depends(get_db)):
    """更新持仓"""
    pos = db.get(UserPosition, position_id)
    if pos is None:
        raise HTTPException(status_code=404, detail="持仓不存在")

    if data.buy_price is not None:
        pos.buy_price = data.buy_price
    if data.quantity is not None:
        pos.quantity = data.quantity
    if data.status is not None:
        pos.status = data.status

    db.commit()
    db.refresh(pos)
    return pos


@router.delete("/{position_id}", status_code=204)
def delete_position(position_id: int, db: Session = Depends(get_db)):
    """删除持仓"""
    pos = db.get(UserPosition, position_id)
    if pos is None:
        raise HTTPException(status_code=404, detail="持仓不存在")
    db.delete(pos)
    db.commit()
