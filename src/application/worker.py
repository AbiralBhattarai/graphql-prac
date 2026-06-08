import logging
from src.domain.models.input import RawDataModel
from src.application.services.data_preprocess import DataPreprocess
from src.adapters.redis_adapter import RedisAdapter
import asyncio

logger = logging.getLogger(__name__)

async def process_worker(task_id: str, raw_data: RawDataModel, redis_adapter: RedisAdapter):
    try:
        
        # Initialize the processing service
        preprocessor = DataPreprocess(raw_data=raw_data)
        
        # Process the data
        processed_data_dict = await preprocessor.process()
        await asyncio.sleep(20)
        
        # Add task_id and status to the dict to save in Redis
        processed_data_dict["task_id"] = task_id
        processed_data_dict["status"] = "completed"

        # Convert booleans to strings to avoid redis-py serialization errors
        processed_data_dict = {k: str(v) if isinstance(v, bool) else v for k, v in processed_data_dict.items()}
        
        # Update Redis key
        key = f"task:{task_id}"
        await redis_adapter.update(key, processed_data_dict)
        logger.info(f"Task {task_id} completed successfully.")
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        # Update status to failed
        key = f"task:{task_id}"
        await redis_adapter.update(key, {"status": "failed", "error": str(e)})
