from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from ..models import User, Wallet
from ..schemas import WalletCreate
from ..dependencies import get_current_user
from ..database import get_db

wallet_router = APIRouter(prefix="/wallets", tags=["wallets"])

@wallet_router.get("/{wallet_id}")
async def get_wallet_by_id(wallet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_wallet = get_wallet(db, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if db_wallet.id_user != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to access this wallet")

    return {"message": "Wallet fetched successfully", "data": {"id_wallet": db_wallet.id_wallet, "balance": db_wallet.balance}, "error": False}


@wallet_router.post("/")
async def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if wallet.id_user != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to create wallet for other user")
    new_wallet = Wallet(balance=wallet.balance, id_user=wallet.id_user)
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return {"message": "Wallet create successfully", "data": {"id_wallet": new_wallet.id_wallet, "balance": new_wallet.balance}, "error": False}

@wallet_router.put("/{wallet_id}/increase_balance")
async def increase_wallet_balance(wallet_id: int, amount: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    db_wallet = get_wallet(db, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    amount_decimal = Decimal(str(amount))
    db_wallet.balance += amount_decimal
    db.commit()
    db.refresh(db_wallet)
    
    return {"message": "Wallet balance increased successfully", "data": {"id_wallet": db_wallet.id_wallet, "balance": db_wallet.balance}, "error": False}

@wallet_router.put("/{wallet_id}/decrease_balance")
async def decrease_wallet_balance(wallet_id: int, amount: float, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    db_wallet = get_wallet(db, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if db_wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    db_wallet.balance -= Decimal(str(amount))
    db.commit()
    db.refresh(db_wallet)
    
    return {"message": "Wallet balance decreased successfully", "data": {"id_wallet": db_wallet.id_wallet, "balance": db_wallet.balance}, "error": False}

@wallet_router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_wallet = delete_wallet(db, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return {"message": "Wallet deleted successfully", "data": {"id_wallet": db_wallet.id_wallet, "balance": db_wallet.balance}, "error": False}


def get_wallet(db: Session, wallet_id: int):
    return db.query(Wallet).filter(Wallet.id_wallet == wallet_id).first()

def delete_wallet(db: Session, wallet_id: int):
    db_wallet = db.query(Wallet).filter(Wallet.id_wallet == wallet_id).first()
    if db_wallet:
        db.delete(db_wallet)
        db.commit()
    return db_wallet