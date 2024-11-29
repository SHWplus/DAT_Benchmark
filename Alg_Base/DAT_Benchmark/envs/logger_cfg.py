import logging
import os

def create_logger(process_id:int)->logging.Logger:
    logger_name = "Logger_Agent"+str(process_id)
    logger_path = "./logs/Agent"+str(process_id)+".log"
    # Delete Exist file
    if os.path.exists(logger_path):
        os.unlink(logger_path)
    # Create Logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    # Create File Handler
    file_handler = logging.FileHandler(logger_path)
    file_handler.setLevel(logging.INFO)
    # Create Formatter and add to file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    # Add file handler to logger
    if not logger.handlers:
        logger.addHandler(file_handler)
    return logger