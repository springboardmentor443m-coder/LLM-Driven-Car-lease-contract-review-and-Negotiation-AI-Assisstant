from models.contract import Contract, db
from typing import List, Dict, Any

class DatabaseHandler:
    def save_contract(self, contract: Contract) -> int:
        """Save contract to database"""
        try:
            db.session.add(contract)
            db.session.commit()
            return contract.id
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_contract_by_id(self, contract_id: int) -> Contract:
        """Retrieve contract by ID"""
        return Contract.query.get(contract_id)
    
    def get_user_contracts(self, user_id: str) -> List[Contract]:
        """Get all contracts for a user"""
        return Contract.query.filter_by(user_id=user_id).all()
    
    def get_contracts_by_ids(self, contract_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple contracts by IDs"""
        contracts = Contract.query.filter(Contract.id.in_(contract_ids)).all()
        return [contract.to_dict() for contract in contracts]
    
    def update_contract_score(self, contract_id: int, score: float) -> bool:
        """Update contract fairness score"""
        try:
            contract = Contract.query.get(contract_id)
            if contract:
                contract.fairness_score = score
                db.session.commit()
                return True
        except Exception as e:
            db.session.rollback()
        return False