import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from VelaFi.event_bus import publish
from VelaFi.models import VelafiCustomer, VelafiKycDocument
from VelaFi.velafi_client import VelafiClient

_log = logging.getLogger(__name__)


class VelafiKycService:
    """Service for handling VelaFi KYC operations."""
    
    def __init__(self, velafi_client: VelafiClient):
        self.velafi_client = velafi_client
    
    async def create_customer(self, db: Session, user_id: str, customer_data: Dict[str, Any]) -> VelafiCustomer:
        """Create a VelaFi customer and persist locally."""
        try:
            # Create customer in VelaFi
            velafi_response = await self.velafi_client.create_customer(customer_data)
            velafi_customer_id = velafi_response.get("id")
            
            if not velafi_customer_id:
                raise ValueError("VelaFi did not return a customer ID")
            
            # Persist locally
            customer = VelafiCustomer(
                user_id=user_id,
                velafi_customer_id=velafi_customer_id,
                first_name=customer_data.get("first_name"),
                last_name=customer_data.get("last_name"),
                email=customer_data.get("email"),
                date_of_birth=customer_data.get("date_of_birth"),
                country=customer_data.get("country"),
                phone=customer_data.get("phone"),
                address=customer_data.get("address"),
                city=customer_data.get("city"),
                state=customer_data.get("state"),
                postal_code=customer_data.get("postal_code"),
                kyc_status="pending"
            )
            
            db.add(customer)
            db.commit()
            db.refresh(customer)
            
            # Publish event
            publish("velafi.customer.created", {
                "user_id": user_id,
                "velafi_customer_id": velafi_customer_id,
                "customer_data": customer_data
            })
            
            _log.info(f"Created VelaFi customer {velafi_customer_id} for user {user_id}")
            return customer
            
        except Exception as e:
            _log.error(f"Failed to create VelaFi customer for user {user_id}: {e}")
            db.rollback()
            raise
    
    async def get_customer(self, db: Session, user_id: str) -> Optional[VelafiCustomer]:
        """Get VelaFi customer record for a user."""
        return db.query(VelafiCustomer).filter(VelafiCustomer.user_id == user_id).first()
    
    async def update_customer(self, db: Session, user_id: str, customer_data: Dict[str, Any]) -> VelafiCustomer:
        """Update VelaFi customer information."""
        customer = await self.get_customer(db, user_id)
        if not customer:
            raise ValueError(f"No VelaFi customer found for user {user_id}")
        
        try:
            # Update in VelaFi
            await self.velafi_client.update_customer(customer.velafi_customer_id, customer_data)
            
            # Update local record
            for key, value in customer_data.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            
            customer.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(customer)
            
            # Publish event
            publish("velafi.customer.updated", {
                "user_id": user_id,
                "velafi_customer_id": customer.velafi_customer_id,
                "customer_data": customer_data
            })
            
            return customer
            
        except Exception as e:
            _log.error(f"Failed to update VelaFi customer for user {user_id}: {e}")
            db.rollback()
            raise
    
    async def create_kyc_session(self, db: Session, user_id: str, kyc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a KYC session for document verification."""
        customer = await self.get_customer(db, user_id)
        if not customer:
            raise ValueError(f"No VelaFi customer found for user {user_id}")
        
        try:
            # Create KYC session in VelaFi
            session_response = await self.velafi_client.create_kyc_session(
                customer.velafi_customer_id, 
                kyc_data
            )
            
            # Update customer status
            customer.kyc_status = "submitted"
            customer.kyc_submitted_at = datetime.utcnow()
            db.commit()
            
            # Publish event
            publish("velafi.kyc.session.created", {
                "user_id": user_id,
                "velafi_customer_id": customer.velafi_customer_id,
                "session_data": session_response
            })
            
            return session_response
            
        except Exception as e:
            _log.error(f"Failed to create KYC session for user {user_id}: {e}")
            db.rollback()
            raise
    
    async def get_kyc_status(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get KYC verification status from VelaFi."""
        customer = await self.get_customer(db, user_id)
        if not customer:
            raise ValueError(f"No VelaFi customer found for user {user_id}")
        
        try:
            # Get status from VelaFi
            status_response = await self.velafi_client.get_kyc_status(customer.velafi_customer_id)
            
            # Update local status if different
            remote_status = status_response.get("status")
            if remote_status and remote_status != customer.kyc_status:
                customer.kyc_status = remote_status
                if remote_status == "approved":
                    customer.kyc_verified_at = datetime.utcnow()
                db.commit()
            
            return status_response
            
        except Exception as e:
            _log.error(f"Failed to get KYC status for user {user_id}: {e}")
            raise
    
    async def upload_document(self, db: Session, user_id: str, document_type: str, file_data: bytes, filename: str, mime_type: str) -> VelafiKycDocument:
        """Upload a KYC document to VelaFi."""
        customer = await self.get_customer(db, user_id)
        if not customer:
            raise ValueError(f"No VelaFi customer found for user {user_id}")
        
        try:
            # Upload to VelaFi
            upload_response = await self.velafi_client.upload_document(
                customer.velafi_customer_id,
                document_type,
                file_data,
                filename
            )
            
            velafi_document_id = upload_response.get("id")
            if not velafi_document_id:
                raise ValueError("VelaFi did not return a document ID")
            
            # Persist document metadata locally
            document = VelafiKycDocument(
                velafi_customer_id=customer.id,
                velafi_document_id=velafi_document_id,
                document_type=document_type,
                filename=filename,
                mime_type=mime_type,
                file_size=len(file_data),
                status="uploaded"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # Publish event
            publish("velafi.document.uploaded", {
                "user_id": user_id,
                "velafi_customer_id": customer.velafi_customer_id,
                "velafi_document_id": velafi_document_id,
                "document_type": document_type,
                "filename": filename
            })
            
            return document
            
        except Exception as e:
            _log.error(f"Failed to upload document for user {user_id}: {e}")
            db.rollback()
            raise
    
    async def list_documents(self, db: Session, user_id: str) -> List[VelafiKycDocument]:
        """List all KYC documents for a user."""
        customer = await self.get_customer(db, user_id)
        if not customer:
            return []
        
        return db.query(VelafiKycDocument).filter(
            VelafiKycDocument.velafi_customer_id == customer.id
        ).all()
    
    async def delete_document(self, db: Session, user_id: str, document_id: str) -> None:
        """Delete a KYC document."""
        customer = await self.get_customer(db, user_id)
        if not customer:
            raise ValueError(f"No VelaFi customer found for user {user_id}")
        
        # Find document locally
        document = db.query(VelafiKycDocument).filter(
            VelafiKycDocument.velafi_customer_id == customer.id,
            VelafiKycDocument.velafi_document_id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Document {document_id} not found for user {user_id}")
        
        try:
            # Delete from VelaFi
            await self.velafi_client.delete_kyc_document(
                customer.velafi_customer_id,
                document_id
            )
            
            # Delete locally
            db.delete(document)
            db.commit()
            
            # Publish event
            publish("velafi.document.deleted", {
                "user_id": user_id,
                "velafi_customer_id": customer.velafi_customer_id,
                "velafi_document_id": document_id
            })
            
        except Exception as e:
            _log.error(f"Failed to delete document {document_id} for user {user_id}: {e}")
            db.rollback()
            raise
    
    async def is_kyc_approved(self, db: Session, user_id: str) -> bool:
        """Check if user's KYC is approved."""
        customer = await self.get_customer(db, user_id)
        if not customer:
            return False
        
        return customer.kyc_status == "approved" 