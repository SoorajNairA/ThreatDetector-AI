"""
Online Learning Training Service

Handles background training tasks:
- Query untrained samples from database
- Run partial_fit on new data
- Save updated model
- Mark samples as trained
- Track performance metrics
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

import numpy as np
from supabase import Client

from .online_learning_classifier import get_online_classifier


class TrainingService:
    """Service for managing online learning training tasks."""
    
    def __init__(self, supabase_client: Client):
        """Initialize training service."""
        self.supabase = supabase_client
        self.classifier = get_online_classifier()
        self.is_training = False
    
    async def train_on_new_data(
        self,
        account_id: Optional[UUID] = None,
        batch_size: int = 100,
        max_samples: int = 1000
    ) -> Dict:
        """
        Train on untrained samples from the database.
        
        Args:
            account_id: Optional account ID to filter by
            batch_size: Number of samples per batch
            max_samples: Maximum total samples to process
            
        Returns:
            Training statistics
        """
        if self.is_training:
            return {
                'status': 'already_training',
                'message': 'Training already in progress'
            }
        
        self.is_training = True
        start_time = datetime.now()
        
        try:
            # Build query - only use consent-verified data
            query = self.supabase.table('training_data').select('*').eq('trained', False).eq('consent_verified', True)
            
            if account_id:
                query = query.eq('account_id', str(account_id))
            
            # Fetch untrained samples
            query = query.limit(max_samples).order('created_at')
            response = query.execute()
            
            if not response.data:
                return {
                    'status': 'no_data',
                    'message': 'No untrained samples available',
                    'samples_trained': 0
                }
            
            samples = response.data
            total_samples = len(samples)
            trained_count = 0
            batch_count = 0
            
            # Train in batches
            for i in range(0, total_samples, batch_size):
                batch = samples[i:i + batch_size]
                
                # Extract features and labels
                X = np.array([s['features'] for s in batch])
                y = np.array([s['label'] for s in batch])
                sample_ids = [s['id'] for s in batch]
                
                # Train on batch
                train_stats = self.classifier.partial_fit(X, y)
                
                # Mark samples as trained
                self.supabase.table('training_data').update({
                    'trained': True,
                    'trained_at': datetime.now().isoformat(),
                    'model_version': train_stats['model_version']
                }).in_('id', sample_ids).execute()
                
                trained_count += len(batch)
                batch_count += 1
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            # Save updated model
            model_path = self.classifier.save_model()
            
            # Record model metadata
            model_metadata = {
                'account_id': str(account_id) if account_id else None,
                'model_version': self.classifier.model_version,
                'model_type': 'sgd_logistic_regression',
                'model_path': model_path,
                'training_samples': self.classifier.training_samples,
                'feature_dim': self.classifier.feature_dim,
                'is_active': True,
                'last_trained_at': datetime.now().isoformat(),
                'metadata': {
                    'batch_size': batch_size,
                    'batches_processed': batch_count
                }
            }
            
            # Deactivate previous models
            if account_id:
                self.supabase.table('model_metadata').update({
                    'is_active': False
                }).eq('account_id', str(account_id)).eq('is_active', True).execute()
            else:
                self.supabase.table('model_metadata').update({
                    'is_active': False
                }).is_('account_id', 'null').eq('is_active', True).execute()
            
            # Insert new model metadata
            self.supabase.table('model_metadata').insert(model_metadata).execute()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'samples_trained': trained_count,
                'batches_processed': batch_count,
                'model_version': self.classifier.model_version,
                'total_training_samples': self.classifier.training_samples,
                'model_path': model_path,
                'elapsed_seconds': elapsed,
                'samples_per_second': trained_count / elapsed if elapsed > 0 else 0
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'samples_trained': 0
            }
        finally:
            self.is_training = False
    
    async def get_training_status(self, account_id: Optional[UUID] = None) -> Dict:
        """Get current training status and statistics."""
        try:
            # Count untrained samples with consent
            query = self.supabase.table('training_data').select('id').eq('trained', False).eq('consent_verified', True)
            if account_id:
                query = query.eq('account_id', str(account_id))
            
            untrained_response = query.execute()
            untrained_count = len(untrained_response.data) if untrained_response.data else 0
            
            # Get active model info
            model_query = self.supabase.table('model_metadata').select('*').eq('is_active', True)
            if account_id:
                model_query = model_query.eq('account_id', str(account_id))
            else:
                model_query = model_query.is_('account_id', 'null')
            
            model_response = model_query.execute()
            active_model = model_response.data[0] if model_response.data else None
            
            return {
                'is_training': self.is_training,
                'untrained_samples': untrained_count,
                'model_version': self.classifier.model_version,
                'total_training_samples': self.classifier.training_samples,
                'last_trained': self.classifier.last_trained.isoformat() if self.classifier.last_trained else None,
                'feature_dim': self.classifier.feature_dim,
                'active_model': active_model,
                'model_loaded': self.classifier.model is not None
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def store_training_sample(
        self,
        account_id: UUID,
        feature_vector: List[float],
        label: str,
        confidence: float = 0.0,
        source: str = 'inference',
        metadata: Optional[Dict] = None,
        consent_verified: bool = False
    ) -> Dict:
        """
        Store a training sample in the database.
        
        Args:
            account_id: Account ID
            feature_vector: Extracted feature vector
            label: Classification label
            confidence: Model confidence
            source: Source of the sample ('inference', 'feedback', 'manual')
            metadata: Additional metadata
            consent_verified: Whether user consent was verified
            
        Returns:
            Created record information
        """
        try:
            record = {
                'account_id': str(account_id),
                'features': feature_vector,
                'label': label,
                'confidence': confidence,
                'model_version': self.classifier.model_version,
                'source': source,
                'metadata': metadata or {},
                'consent_verified': consent_verified
            }
            
            response = self.supabase.table('training_data').insert(record).execute()
            
            return {
                'status': 'success',
                'record_id': response.data[0]['id'] if response.data else None
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def apply_feedback(
        self,
        record_id: UUID,
        corrected_label: str,
        retrain: bool = False
    ) -> Dict:
        """
        Apply feedback to correct a label.
        
        Args:
            record_id: Training data record ID
            corrected_label: Corrected label
            retrain: Whether to immediately retrain on this sample
            
        Returns:
            Update status
        """
        try:
            # Update the record
            update_data = {
                'label': corrected_label,
                'feedback_corrected': True,
                'trained': False,  # Mark as untrained so it gets picked up
                'source': 'feedback'
            }
            
            response = self.supabase.table('training_data').update(
                update_data
            ).eq('id', str(record_id)).execute()
            
            if not response.data:
                return {
                    'status': 'error',
                    'message': 'Record not found'
                }
            
            # Optionally retrain immediately
            if retrain and response.data:
                record = response.data[0]
                X = np.array([record['features']])
                y = np.array([record['label']])
                
                train_stats = self.classifier.partial_fit(X, y)
                
                # Mark as trained
                self.supabase.table('training_data').update({
                    'trained': True,
                    'trained_at': datetime.now().isoformat(),
                    'model_version': train_stats['model_version']
                }).eq('id', str(record_id)).execute()
                
                # Save model
                self.classifier.save_model()
                
                return {
                    'status': 'success',
                    'message': 'Feedback applied and retrained',
                    'train_stats': train_stats
                }
            
            return {
                'status': 'success',
                'message': 'Feedback applied, will train in next batch'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# Global training service instance
_training_service = None


def get_training_service(supabase_client: Optional[Client] = None) -> TrainingService:
    """Get or create training service instance."""
    global _training_service
    if _training_service is None and supabase_client:
        _training_service = TrainingService(supabase_client)
    if _training_service is None:
        raise RuntimeError("Training service not initialized. Provide supabase_client.")
    return _training_service
